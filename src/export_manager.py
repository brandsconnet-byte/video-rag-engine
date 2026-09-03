"""Export and clip extraction management."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class ExportManager:
    """Handles clip extraction and export to various formats."""

    def __init__(self, output_config: Dict[str, Any], router_config: Dict[str, Any]):
        """Initialize export manager.
        
        Args:
            output_config: Output configuration
            router_config: Router configuration (for export methods)
        """
        self.output_dir = output_config.get("output_dir", "./extracted_clips")
        self.organize_by_query = output_config.get("organize_by_query", True)
        self.file_naming = output_config.get("file_naming", "{query}_{timestamp}_{index}")
        self.preserve_metadata = output_config.get("preserve_metadata", True)
        self.generate_contact_sheet = output_config.get("generate_contact_sheet", True)
        
        self.router_config = router_config
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Export manager initialized. Output: {self.output_dir}")

    def extract_with_ffmpeg(self, video_path: str, start_time: float, end_time: float, output_dir: Optional[str] = None) -> Optional[str]:
        """Extract clip using FFmpeg.
        
        Args:
            video_path: Path to source video
            start_time: Start time in seconds
            end_time: End time in seconds
            output_dir: Optional output directory override
            
        Returns:
            Path to extracted clip or None on failure
        """
        output_dir = output_dir or self.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        duration = end_time - start_time
        filename = f"clip_{int(start_time)}_{int(end_time)}.mp4"
        output_path = os.path.join(output_dir, filename)
        
        try:
            import ffmpeg
            
            ffmpeg.input(video_path, ss=start_time, t=duration).output(output_path, c='copy').run(quiet=True, overwrite_output=True)
            
            logger.info(f"Extracted clip via FFmpeg: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"FFmpeg extraction failed: {e}")
            return None

    def extract_with_auto_editor(self, video_path: str, start_time: float, end_time: float, output_dir: Optional[str] = None) -> Optional[str]:
        """Extract and optimize clip using auto-editor.
        
        Args:
            video_path: Path to source video
            start_time: Start time in seconds
            end_time: End time in seconds
            output_dir: Optional output directory override
            
        Returns:
            Path to optimized clip or None on failure
        """
        output_dir = output_dir or self.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        duration = end_time - start_time
        filename = f"clip_optimized_{int(start_time)}_{int(end_time)}.mp4"
        output_path = os.path.join(output_dir, filename)
        
        try:
            import subprocess
            import shutil
            
            # Check if auto-editor is installed
            if not shutil.which("auto-editor"):
                logger.warning("auto-editor not found in PATH. Falling back to FFmpeg.")
                return self.extract_with_ffmpeg(video_path, start_time, end_time, output_dir)
            
            # First extract the segment with FFmpeg
            temp_segment = os.path.join(output_dir, f"temp_segment_{int(start_time)}_{int(end_time)}.mp4")
            segment_duration = end_time - start_time
            
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-ss", str(start_time), "-t", str(segment_duration),
                "-c", "copy", temp_segment
            ]
            
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
            
            # Apply auto-editor to remove silence and static frames
            auto_editor_config = self.router_config.get("auto_editor", {})
            margin = auto_editor_config.get("margin", "0.2sec")
            
            ae_cmd = [
                "auto-editor", temp_segment,
                "--output", output_path,
                "--margin", margin,
                "--no-open"
            ]
            
            logger.info(f"Running auto-editor on segment: {temp_segment}")
            subprocess.run(ae_cmd, check=True, capture_output=True, text=True)
            
            # Clean up temp segment
            if os.path.exists(temp_segment):
                os.remove(temp_segment)
            
            logger.info(f"Optimized clip via auto-editor: {output_path}")
            return output_path
        
        except subprocess.CalledProcessError as e:
            logger.error(f"auto-editor command failed: {e.stderr}")
            # Fallback to FFmpeg
            logger.info("Falling back to FFmpeg extraction")
            return self.extract_with_ffmpeg(video_path, start_time, end_time, output_dir)
        except Exception as e:
            logger.error(f"auto-editor extraction failed: {e}")
            return None

    def generate_edl(self, results: list, output_path: str, video_path: str = "", format_type: str = "fcpxml") -> Optional[str]:
        """Generate EDL/XML for professional editing.
        
        Args:
            results: Search results
            output_path: Path to save EDL file
            video_path: Path to source video for metadata
            format_type: Export format - 'fcpxml' (Final Cut Pro), 'premiere' (Adobe Premiere), 'edl' (generic)
            
        Returns:
            Path to generated EDL file or None on failure
        """
        try:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            
            if format_type == "fcpxml":
                return self._generate_fcpxml(results, output_path, video_path)
            elif format_type == "premiere":
                return self._generate_premiere_xml(results, output_path, video_path)
            else:
                return self._generate_generic_edl(results, output_path)
        
        except Exception as e:
            logger.error(f"EDL generation failed: {e}")
            return None

    def _generate_fcpxml(self, results: list, output_path: str, video_path: str) -> Optional[str]:
        """Generate Final Cut Pro XML (FCPXML) format."""
        try:
            from lxml import etree
            
            # Get video info
            duration = results[-1]["end_time"] if results else 0
            video_name = os.path.basename(video_path) if video_path else "video.mp4"
            
            # Create FCPXML structure
            fcpxml = etree.Element("fcpxml", version="1.9")
            
            # Resources
            resources = etree.SubElement(fcpxml, "resources")
            format_elem = etree.SubElement(resources, "format", 
                id="r1", 
                name="FFVideoFormat1080p30", 
                frameDuration="1/30s",
                width="1920", 
                height="1080"
            )
            
            # Asset reference
            asset = etree.SubElement(resources, "asset",
                id="r2",
                name=video_name,
                src=f"file://{os.path.abspath(video_path)}" if video_path else "",
                start="0s",
                duration=f"{duration}s"
            )
            
            # Library and Event
            library = etree.SubElement(fcpxml, "library")
            event = etree.SubElement(library, "event", name="Video RAG Export")
            
            # Project
            project = etree.SubElement(event, "project", name="Extracted Scenes")
            sequence = etree.SubElement(project, "sequence", format="r1")
            spine = etree.SubElement(sequence, "spine")
            
            # Add clips
            for i, result in enumerate(results):
                start_time = result.get("start_time", 0)
                end_time = result.get("end_time", 0)
                clip_duration = end_time - start_time
                
                clip = etree.SubElement(spine, "clip",
                    name=f"Scene {result.get('scene_id', i)}",
                    offset=f"{start_time}s",
                    duration=f"{clip_duration}s",
                    start=f"{start_time}s"
                )
                
                # Video reference
                video_elem = etree.SubElement(clip, "video", ref="r2")
                
                # Add tags as keywords
                tags = result.get("yolo_tags", [])
                if tags:
                    keywords = etree.SubElement(clip, "keywords")
                    for tag in tags:
                        etree.SubElement(keywords, "keyword", value=tag)
            
            # Write to file
            tree = etree.ElementTree(fcpxml)
            tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
            
            logger.info(f"Generated FCPXML: {output_path}")
            return output_path
            
        except ImportError:
            logger.warning("lxml not installed. Install with: pip install lxml")
            return self._generate_generic_edl(results, output_path)
        except Exception as e:
            logger.error(f"FCPXML generation failed: {e}")
            return None

    def _generate_premiere_xml(self, results: list, output_path: str, video_path: str) -> Optional[str]:
        """Generate Adobe Premiere XML format."""
        try:
            from lxml import etree
            
            video_name = os.path.basename(video_path) if video_path else "video.mp4"
            
            # Create Premiere XML structure
            premiere = etree.Element("PremiereData", version="3")
            project = etree.SubElement(premiere, "Project")
            
            # Sequence
            sequence = etree.SubElement(project, "Sequence", name="Video RAG Export")
            timeline = etree.SubElement(sequence, "Timeline")
            
            # Video track
            video_track = etree.SubElement(timeline, "Track", type="video")
            
            # Add clips
            for i, result in enumerate(results):
                start_time = result.get("start_time", 0)
                end_time = result.get("end_time", 0)
                clip_duration = end_time - start_time
                
                clip_item = etree.SubElement(video_track, "ClipItem",
                    id=f"clip_{i}"
                )
                
                etree.SubElement(clip_item, "Name").text = f"Scene {result.get('scene_id', i)}"
                etree.SubElement(clip_item, "Start").text = str(int(start_time * 30))  # Frames at 30fps
                etree.SubElement(clip_item, "End").text = str(int(end_time * 30))
                etree.SubElement(clip_item, "Duration").text = str(int(clip_duration * 30))
                
                # File reference
                file_elem = etree.SubElement(clip_item, "File", id=f"file_{i}")
                etree.SubElement(file_elem, "Name").text = video_name
                etree.SubElement(file_elem, "Path").text = os.path.abspath(video_path) if video_path else ""
                
                # Tags as comments
                tags = result.get("yolo_tags", [])
                if tags:
                    etree.SubElement(clip_item, "Comment").text = ", ".join(tags)
            
            # Write to file
            tree = etree.ElementTree(premiere)
            tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
            
            logger.info(f"Generated Premiere XML: {output_path}")
            return output_path
            
        except ImportError:
            logger.warning("lxml not installed. Install with: pip install lxml")
            return self._generate_generic_edl(results, output_path)
        except Exception as e:
            logger.error(f"Premiere XML generation failed: {e}")
            return None

    def _generate_generic_edl(self, results: list, output_path: str) -> Optional[str]:
        """Generate generic CMX3600 EDL format."""
        try:
            with open(output_path, 'w') as f:
                f.write("TITLE: Video RAG Engine Export\n")
                f.write("FCM: NON-DROP FRAME\n\n")
                
                for i, result in enumerate(results, 1):
                    start_time = result.get("start_time", 0)
                    end_time = result.get("end_time", 0)
                    
                    # Convert to timecode (HH:MM:SS:FF at 30fps)
                    def to_tc(seconds):
                        h = int(seconds // 3600)
                        m = int((seconds % 3600) // 60)
                        s = int(seconds % 60)
                        f = int((seconds % 1) * 30)
                        return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"
                    
                    src_in = to_tc(start_time)
                    src_out = to_tc(end_time)
                    rec_in = to_tc(start_time)
                    rec_out = to_tc(end_time)
                    
                    f.write(f"{i:03d}  AX       V     C        {src_in} {src_out} {rec_in} {rec_out}\n")
                    
                    tags = result.get("yolo_tags", [])
                    if tags:
                        f.write(f"* FROM CLIP NAME: Scene {result.get('scene_id', i)}\n")
                        f.write(f"* TAGS: {', '.join(tags)}\n")
                    f.write("\n")
            
            logger.info(f"Generated generic EDL: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Generic EDL generation failed: {e}")
            return None
