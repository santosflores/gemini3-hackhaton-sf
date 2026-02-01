import logging
import json
import os
from pathlib import Path
from google.adk import Agent
from google.adk.tools import FunctionTool
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

def generate_play_visual(analysis_paragraph: str) -> str:
    """Generate a visual diagram or illustration of a football play based on its text analysis.
    
    Args:
        analysis_paragraph: The detailed text analysis of the football play.
        
    Returns:
        A success message with the path to the generated image or an error message.
    """
    logger.info("generate_play_visual called")
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return json.dumps({
                "status": "error",
                "message": "GEMINI_API_KEY environment variable not set."
            })
            
        client = genai.Client(api_key=api_key)
        
        prompt = f"A professional NFL-style playbook diagram of a football play. Detailed schematic with Xs and Os, arrows for routes, and blocking schemes. Based on this analysis: {analysis_paragraph}. Tactical, clean, 2D top-down view, whiteboard aesthetic."
        
        # Use generate_content for multimodal image generation as per docs
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
            )
        )
        
        # Collect generated images
        images = []
        for part in response.parts:
            if part.inline_data:
                images.append(part.as_image())
        
        if not images:
            return json.dumps({
                "status": "error",
                "message": f"No image generated. Response parts: {[type(p) for p in response.parts]}"
            })
            
        # Save images to the uploads directory in the project root
        uploads_dir = PROJECT_ROOT / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        saved_paths = []
        relative_paths = []
        for i, img in enumerate(images):
            file_name = f"play_visual_{timestamp}_{i}.png"
            file_path = uploads_dir / file_name
            img.save(str(file_path))
            saved_paths.append(str(file_path))
            relative_paths.append(file_name)
        
        return json.dumps({
            "status": "success",
            "message": f"Generated {len(saved_paths)} play visualizations.",
            "image_paths": saved_paths,
            "image_filenames": relative_paths,
            "prompt_used": prompt
        })
        
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Error generating visualization: {str(e)}"
        })

generate_visual_tool = FunctionTool(func=generate_play_visual)

nanoBananaAgent = Agent(
    name="nanoBananaAgent",
    model="gemini-3-pro-image-preview", # Using a standard model for the agent logic
    description="An agent that creates visual playbook diagrams for football plays.",
    instruction="You are a visualization specialist for football coaching. When provided with a play analysis, use the `generate_visual_tool` to create a professional diagram. Always confirm when the visualization is ready.",
    tools=[generate_visual_tool],
    output_key="image_paths"
)
