import os
import warnings
# Suppress all warnings globally
warnings.filterwarnings("ignore")

os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '0'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '1'

import gradio as gr
import sys

from core import core
from core.core import _, get_available_languages

import main
import models

from transformers import logging as hf_logging
# Suppress warnings and info messages from Hugging Face
hf_logging.set_verbosity_error()

def update_language(new_lang):
    """Updates the global language and saves it to config."""
    core.ui_language = new_lang
    # Save the new language to wui.json
    core.save_wui(language=new_lang)
    # Notify the user that a restart is needed
    gr.Info("Language preference saved! Please restart the app to apply the new language.")
    
def get_header_text():
    """Helper to format the header string safely."""
    p_name = core.project_name if core.project_name else "None"
    u_name = core.user_name if core.user_name else "None"
    return f"# {_('APP')} / {_('USER')} : {u_name} / {_('PROJECT')} : {p_name}"
    
def refresh_project_state(current_selection):
    """Called when user manually selects a project from the dropdown."""
    projects = core.list_projects()

    if current_selection in projects:
        core.project_name = current_selection
        core.project_path = os.path.join(core.p_path, current_selection)
        final_value = current_selection
        core.save_wui(last_project=final_value)
    else:
        # If selection is invalid, try to auto-select the first available
        if len(projects) > 0:
            final_value = projects[0]
            core.project_name = final_value
            core.project_path = os.path.join(core.p_path, final_value)
            core.save_wui(last_project=final_value)
        else:
            final_value = None
            core.project_name = None
            core.project_path = core.p_path

    return (gr.Dropdown(choices=projects, value=final_value), get_header_text())

def refresh_project_folder(current_selection):
    """
    Called automatically by the Timer every 5 seconds.
    Checks disk for new/deleted folders, updates list, and AUTO-SELECTS if needed.
    """
    projects = core.list_projects()
    
    if current_selection in projects:
        final_value = current_selection
        core.project_path = os.path.join(core.p_path, current_selection)
    elif len(projects) > 0:
        final_value = projects[0]
        core.project_name = final_value
        core.project_path = os.path.join(core.p_path, final_value)
        core.save_wui(last_project=final_value)
    else:
        final_value = None
        core.project_name = None
        core.project_path = core.p_path

    # Sync Global State
    core.project_name = final_value

    # Return new Dropdown AND update the Header so it matches the auto-selection
    return (
        gr.Dropdown(choices=projects, value=final_value),
        get_header_text()
    )

def refresh_user_state(current_selection):
    """Called when user manually selects a user from the dropdown."""
    users = core.list_users()

    # Determine User
    if current_selection in users:
        core.user_name = current_selection
    elif len(users) > 0:
        core.user_name = users[0]
    else:
        core.user_name = None

    if core.user_name:
        core.user_path = os.path.join(core.u_path, core.user_name)
        
        # Shift Project Path to New User
        core.p_path = os.path.join(core.user_path, "projects")
        os.makedirs(core.p_path, exist_ok=True)
        
        projects = core.list_projects()
        if not projects:
            os.makedirs(os.path.join(core.p_path, "myproject"), exist_ok=True)
            projects = ["myproject"]
            
        final_proj = core.project_name if core.project_name in projects else projects[0]
        
        core.project_name = final_proj
        core.project_path = os.path.join(core.p_path, final_proj)
        core.save_wui(last_user=core.user_name, last_project=final_proj)
        
        return (
            gr.Dropdown(choices=users, value=core.user_name), 
            gr.Dropdown(choices=projects, value=final_proj), 
            get_header_text()
        )
    return (gr.update(), gr.update(), get_header_text())

with gr.Blocks() as root_demo:
    
    with gr.Row():
        with gr.Column(scale=3):
            header_md = gr.Markdown(value=get_header_text())
            
        with gr.Column(scale=2):
            with gr.Row():
                existing_users = core.list_users()
                user_selector = gr.Dropdown(
                    choices=existing_users, 
                    show_label=False,
                    value=core.user_name, 
                    interactive=True,
                    container=False
                )
                
                existing_projects = core.list_projects()
                project_selector = gr.Dropdown(
                    choices=existing_projects, 
                    show_label=False,
                    value=core.project_name, 
                    interactive=True,
                    container=False
                )       

                language_selector = gr.Dropdown(
                    choices=get_available_languages(), 
                    value=core.ui_language,
                    show_label=False,
                    interactive=True,
                    container=False
                )
    
    #################################################
    
    with gr.Tabs():
        
        with gr.Tab(_("HOME")):
            main.create_demo(project_selector, user_selector, header_md)
            
        with gr.Tab(_("MODELS")):
            models.create_models_tab()


    #################################################
     
    user_selector.change(
        fn=refresh_user_state, 
        inputs=user_selector, 
        outputs=[user_selector, project_selector, header_md]
    )

    project_selector.change(
        fn=refresh_project_state, 
        inputs=project_selector, 
        outputs=[project_selector, header_md]
    )

    language_selector.change(
        fn=update_language,
        inputs=language_selector,
        outputs=None
    )    

    refresh_timer = gr.Timer(value=5.0)
    
    refresh_timer.tick(
        fn=refresh_project_folder, 
        inputs=project_selector, 
        outputs=[project_selector, header_md] 
    )  

if __name__ == "__main__":
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "css", "gradio.css")
    root_demo.launch(css=css_path)