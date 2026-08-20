import gradio as gr
import os
import sys
import shutil
import platform

from core import core
from core.core import _
import psutil
import pynvml

def get_system_stats_html():
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent
    
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        vram_percent = round((info.used / info.total) * 100, 1)
        gpu_percent = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
    except Exception:
        vram_percent = 0.0
        gpu_percent = 0.0
        
    
    html = f"""
    <div style="display: flex; flex-direction: column; gap: 12px; padding: 10px 0; font-family: monospace;">
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 13px; color: var(--body-text-color);">
                <span>{_('HOME_CPU_USAGE')}</span>
                <span>{cpu_percent}%</span>
            </div>
            <div style="width: 100%; height: 14px; background-color: var(--background-fill-secondary); border-radius: 8px; border: 1px solid var(--border-color-primary);">
                <div style="height: 100%; border-radius: 6px; transition: clip-path 0.5s ease-out; background: linear-gradient(90deg, #4caf50, #ffeb3b, #f44336); clip-path: inset(0 {100 - cpu_percent}% 0 0 round 6px);"></div>
            </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 13px; color: var(--body-text-color);">
                <span>{_('HOME_RAM_USAGE')}</span>
                <span>{ram_percent}%</span>
            </div>
            <div style="width: 100%; height: 14px; background-color: var(--background-fill-secondary); border-radius: 8px; border: 1px solid var(--border-color-primary);">
                <div style="height: 100%; border-radius: 6px; transition: clip-path 0.5s ease-out; background: linear-gradient(90deg, #2196f3, #9c27b0, #f44336); clip-path: inset(0 {100 - ram_percent}% 0 0 round 6px);"></div>
            </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 13px; color: var(--body-text-color);">
                <span>{_('HOME_GPU_USAGE')}</span>
                <span>{gpu_percent}%</span>
            </div>
            <div style="width: 100%; height: 14px; background-color: var(--background-fill-secondary); border-radius: 8px; border: 1px solid var(--border-color-primary);">
                <div style="height: 100%; border-radius: 6px; transition: clip-path 0.5s ease-out; background: linear-gradient(90deg, #4caf50, #ffeb3b, #f44336); clip-path: inset(0 {100 - gpu_percent}% 0 0 round 6px);"></div>
            </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 13px; color: var(--body-text-color);">
                <span>{_('HOME_VRAM_USAGE')}</span>
                <span>{vram_percent}%</span>
            </div>
            <div style="width: 100%; height: 14px; background-color: var(--background-fill-secondary); border-radius: 8px; border: 1px solid var(--border-color-primary);">
                <div style="height: 100%; border-radius: 6px; transition: clip-path 0.5s ease-out; background: linear-gradient(90deg, #2196f3, #9c27b0, #f44336); clip-path: inset(0 {100 - vram_percent}% 0 0 round 6px);"></div>
            </div>
        </div>
    </div>
    """
    return html

def get_static_and_project_info():
    """Gets active project info."""
    # Project Info
    if core.project_name:
        proj_path = os.path.join(core.p_path, core.project_name)
    else:
        proj_path = "None"
        
    if core.project_name and os.path.exists(proj_path):
        file_count = 0
        total_size = 0
        try:
            for dp, _dirs, fn in os.walk(proj_path):
                for f in fn:
                    file_count += 1
                    total_size += os.path.getsize(os.path.join(dp, f))
            
            size_mb = round(total_size / (1024**2), 2)
            proj_status = (f"✅ {_('HOME_ACTIVE_PROJECT')}: {core.project_name}\n"
                           f"📂 {_('HOME_LOCATION')}: {proj_path}\n"
                           f"📄 {_('HOME_FILES')}: {file_count}\n"
                           f"📦 {_('HOME_SIZE')}: {size_mb} MB")
        except Exception as e:
            proj_status = f"✅ {_('HOME_ACTIVE')}: {core.project_name}\n❌ {_('HOME_ERROR_SCANNING')}: {e}"
    else:
        proj_status = f"⚠️ {_('HOME_NO_ACTIVE_PROJECT')}"

    return proj_status

def create_user_fn(new_name):
    if not new_name or not new_name.strip():
        return gr.update(), gr.update(), gr.update(), "❌ Error: Name cannot be empty."
    
    clean_name = new_name.strip()
    new_path = os.path.join(core.u_path, clean_name)
    
    if os.path.exists(new_path):
        return gr.update(), gr.update(), gr.update(), f"❌ Error: User '{clean_name}' already exists."
        
    try:
        os.makedirs(new_path)
        core.user_name = clean_name
        core.user_path = new_path
        
        # Initialize default project for the newly created user
        core.p_path = os.path.join(new_path, "projects")
        os.makedirs(os.path.join(core.p_path, "myproject"), exist_ok=True)
        core.project_name = "myproject"
        core.project_path = os.path.join(core.p_path, "myproject")
        
        core.save_wui(last_user=clean_name, last_project="myproject")
        
        new_list = core.list_users()
        user_dd_update = gr.Dropdown(choices=new_list, value=clean_name)
        proj_dd_update = gr.Dropdown(choices=["myproject"], value="myproject")
        
        hd_update = f"# {_('APP')} / USER : {clean_name} / {_('PROJECT')} : myproject"
        
        return user_dd_update, proj_dd_update, hd_update, f"✅ Created User: {clean_name}"
    except Exception as e:
        return gr.update(), gr.update(), gr.update(), f"❌ System Error: {str(e)}"


def rename_user_fn(new_name):
    if not new_name or not new_name.strip():
        return gr.update(), gr.update(), gr.update(), "❌ Error: Name cannot be empty."
    if not core.user_name:
         return gr.update(), gr.update(), gr.update(), "❌ Error: No user selected."

    clean_name = new_name.strip()
    old_path = core.user_path
    new_path = os.path.join(core.u_path, clean_name)
    
    if os.path.exists(new_path):
        return gr.update(), gr.update(), gr.update(), f"❌ Error: Folder '{clean_name}' already exists."
    
    try:
        os.rename(old_path, new_path)
        core.user_name = clean_name
        core.user_path = new_path
        
        # Shift project mapping to renamed folder
        core.p_path = os.path.join(new_path, "projects")
        if core.project_name:
            core.project_path = os.path.join(core.p_path, core.project_name)
        
        core.save_wui(last_user=clean_name)
        new_list = core.list_users()
        user_dd_update = gr.Dropdown(choices=new_list, value=clean_name)
        proj_dd_update = gr.update() # Projects inside remain unaffected
        
        p_name = core.project_name if core.project_name else "None"
        hd_update = f"# {_('APP')} / USER : {clean_name} / {_('PROJECT')} : {p_name}"
        
        return user_dd_update, proj_dd_update, hd_update, f"✅ Renamed User to: {clean_name}"
    except Exception as e:
        return gr.update(), gr.update(), gr.update(), f"❌ System Error: {str(e)}"
        
def delete_user_fn(confirm_name):
    if not core.user_name:
        return gr.update(), gr.update(), gr.update(), "❌ Error: No active user."
    
    if confirm_name != core.user_name:
        return gr.update(), gr.update(), gr.update(), f"❌ Error: Name '{confirm_name}' does not match active user."

    target_name = core.user_name
    try:
        if core.delete_user(target_name):
            remaining = core.list_users()
            if not remaining:
                os.makedirs(os.path.join(core.u_path, "artha"), exist_ok=True)
                remaining = ["artha"]
            
            new_active = remaining[0]
            core.user_name = new_active
            core.user_path = os.path.join(core.u_path, new_active)
            
            # Cascade path reset for the new active user's projects
            core.p_path = os.path.join(core.user_path, "projects")
            os.makedirs(core.p_path, exist_ok=True)
            projects = core.list_projects()
            if not projects:
                os.makedirs(os.path.join(core.p_path, "myproject"), exist_ok=True)
                projects = ["myproject"]
            
            new_proj = projects[0]
            core.project_name = new_proj
            core.project_path = os.path.join(core.p_path, new_proj)
            
            core.save_wui(last_user=new_active, last_project=new_proj)
            
            user_dd_update = gr.Dropdown(choices=remaining, value=new_active)
            proj_dd_update = gr.Dropdown(choices=projects, value=new_proj)
            
            hd_update = f"# {_('APP')} / USER : {new_active} / {_('PROJECT')} : {new_proj}"
            return user_dd_update, proj_dd_update, hd_update, f"🗑️ Deleted user: {target_name}"
        else:
            return gr.update(), gr.update(), gr.update(), "❌ Error: User folder not found."
    except Exception as e:
        return gr.update(), gr.update(), gr.update(), f"❌ System Error: {str(e)}"
        
def create_project_fn(new_name):
    if not new_name or not new_name.strip():
        return gr.update(), gr.update(), "❌ Error: Name cannot be empty."
    
    clean_name = new_name.strip()
    new_path = os.path.join(core.p_path, clean_name)
    
    if os.path.exists(new_path):
        return gr.update(), gr.update(), f"❌ Error: Project '{clean_name}' already exists."
        
    try:
        os.makedirs(new_path)
        core.project_name = clean_name
        core.project_path = new_path
        
        core.save_wui(last_project=clean_name)
        
        new_project_list = core.list_projects()
        dd_update = gr.Dropdown(choices=new_project_list, value=clean_name)
        
        u_name = core.user_name if core.user_name else "None"
        hd_update = f"# {_('APP')} / USER : {u_name} / {_('PROJECT')} : {clean_name}"
        
        return dd_update, hd_update, f"✅ Created: {clean_name}"
    except Exception as e:
        return gr.update(), gr.update(), f"❌ System Error: {str(e)}"
        
def rename_project_fn(new_name):
    if not new_name or not new_name.strip():
        return gr.update(), gr.update(), "❌ Error: Name cannot be empty."
    
    if not core.project_name:
         return gr.update(), gr.update(), "❌ Error: No project selected to rename."

    clean_name = new_name.strip()
    old_path = core.project_path
    new_path = os.path.join(core.p_path, clean_name)
    
    if os.path.exists(new_path):
        return gr.update(), gr.update(), f"❌ Error: Folder '{clean_name}' already exists."
    
    try:
        os.rename(old_path, new_path)
        core.project_name = clean_name
        core.project_path = new_path
        
        core.save_wui(last_project=clean_name)
        
        new_project_list = core.list_projects()
        dd_update = gr.Dropdown(choices=new_project_list, value=clean_name)
        
        u_name = core.user_name if core.user_name else "None"
        hd_update = f"# {_('APP')} / USER : {u_name} / {_('PROJECT')} : {clean_name}"
        
        return dd_update, hd_update, f"✅ Renamed to: {clean_name}"
    except Exception as e:
        return gr.update(), gr.update(), f"❌ System Error: {str(e)}"
        
def delete_project_fn(confirm_name):
    if not core.project_name:
        return gr.update(), gr.update(), "❌ Error: No active project."
    
    if confirm_name != core.project_name:
        return gr.update(), gr.update(), f"❌ Error: Name '{confirm_name}' does not match active project."

    target_name = core.project_name
    try:
        if core.delete_project(target_name):
            remaining = core.list_projects()
            if not remaining:
                os.makedirs(os.path.join(core.p_path, "myproject"), exist_ok=True)
                remaining = ["myproject"]
            
            new_active = remaining[0]
            core.project_name = new_active
            core.project_path = os.path.join(core.p_path, new_active)
            
            core.save_wui(last_project=new_active)
            
            dd_update = gr.Dropdown(choices=remaining, value=new_active)
            
            u_name = core.user_name if core.user_name else "None"
            hd_update = f"# {_('APP')} / USER : {u_name} / {_('PROJECT')} : {new_active}"
            return dd_update, hd_update, f"🗑️ Deleted project: {target_name}"
        else:
            return gr.update(), gr.update(), "❌ Error: Project folder not found."
    except Exception as e:
        return gr.update(), gr.update(), f"❌ System Error: {str(e)}"

# ======================================================
# UI CREATION
# ======================================================

def create_demo(project_selector=None, user_selector=None, header_md=None):
    
    with gr.Blocks() as demo:
        
        with gr.Row():
            
            # --------------------------------------------------
            # COLUMN 1: User Management
            # --------------------------------------------------
            with gr.Column(scale=1, variant="panel"):
                gr.Markdown(_("HOME_USER_MANAGEMENT"))
                with gr.Row():
                    create_user_input = gr.Textbox(placeholder=_("HOME_PLACEHOLDER_NEW_USER"), show_label=False, container=False, scale=3)
                    create_user_btn = gr.Button(_("HOME_BTN_CREATE_USER"), variant="primary", scale=1)
                with gr.Row():
                    rename_user_input = gr.Textbox(placeholder=_("HOME_PLACEHOLDER_RENAME_USER"), show_label=False, container=False, scale=3)
                    rename_user_btn = gr.Button(_("HOME_BTN_RENAME_USER"), variant="secondary", scale=1)
                user_log = gr.Textbox(label=_("HOME_USER_STATUS"), lines=1, interactive=False)

                with gr.Accordion(_("HOME_USER_DANGER_ZONE"), open=False):
                    gr.Markdown(_("HOME_DELETE_USER_CONFIRM_TEXT"))
                    delete_user_input = gr.Textbox(placeholder=_("HOME_PLACEHOLDER_DELETE_USER"), show_label=False)
                    delete_user_btn = gr.Button(_("HOME_BTN_DELETE_USER"), variant="stop")
                    delete_user_log = gr.Textbox(label=_("HOME_USER_DELETION_STATUS"), lines=1, interactive=False)
                
                gr.HTML("<hr>")
                gr.Markdown(_("HOME_SYSTEM_RESOURCES"))
                sys_monitor_html = gr.HTML(get_system_stats_html())
                sys_timer = gr.Timer(2)
                sys_timer.tick(get_system_stats_html, outputs=[sys_monitor_html])

                
            # --------------------------------------------------
            # COLUMN 2: Project Management & Active Data & Hardware Env
            # --------------------------------------------------
            with gr.Column(scale=1, variant="panel"):
                gr.Markdown(_("HOME_PROJECT_MANAGEMENT"))
                with gr.Row():
                    create_name_input = gr.Textbox(placeholder=_("HOME_PLACEHOLDER_NEW_PROJECT"), show_label=False, container=False, scale=3)
                    create_btn = gr.Button(_("HOME_BTN_CREATE"), variant="primary", scale=1)
                with gr.Row():
                    rename_name_input = gr.Textbox(placeholder=_("HOME_PLACEHOLDER_RENAME"), show_label=False, container=False, scale=3)
                    rename_btn = gr.Button(_("HOME_BTN_RENAME"), variant="secondary", scale=1)
                project_log = gr.Textbox(label=_("HOME_STATUS"), lines=1, interactive=False)

                with gr.Accordion(_("HOME_DANGER_ZONE"), open=False):
                    gr.Markdown(_("HOME_DELETE_CONFIRM_TEXT"))
                    delete_confirm_input = gr.Textbox(placeholder=_("HOME_PLACEHOLDER_DELETE"), show_label=False)
                    delete_btn = gr.Button(_("HOME_BTN_DELETE"), variant="stop")
                    delete_log = gr.Textbox(label=_("HOME_DELETION_STATUS"), lines=1, interactive=False)

                gr.HTML("<hr>")

                # Active Project Data
                gr.Markdown(_("HOME_ACTIVE_PROJ_DATA"))
                proj_box = gr.Textbox(label=_("HOME_PROJ_DETAILS"), lines=5)
                refresh_btn = gr.Button(_("HOME_BTN_REFRESH"), variant="secondary")





        # Output group for refresh functions
        info_outputs = [proj_box]

        # --- LOGIC ---
        if project_selector is not None and user_selector is not None and header_md is not None:
            create_user_btn.click(create_user_fn, inputs=[create_user_input], outputs=[user_selector, project_selector, header_md, user_log])
            rename_user_btn.click(rename_user_fn, inputs=[rename_user_input], outputs=[user_selector, project_selector, header_md, user_log])
            
            create_btn.click(create_project_fn, inputs=[create_name_input], outputs=[project_selector, header_md, project_log]).success(get_static_and_project_info, outputs=info_outputs)
            rename_btn.click(rename_project_fn, inputs=[rename_name_input], outputs=[project_selector, header_md, project_log]).success(get_static_and_project_info, outputs=info_outputs)
            delete_btn.click(
                delete_project_fn, 
                inputs=[delete_confirm_input], 
                outputs=[project_selector, header_md, delete_log]
            ).success(
                get_static_and_project_info, 
                outputs=info_outputs
            )
            

        
        else:
            fb_user = lambda x: (gr.update(), gr.update(), gr.update(), "⚠️ Run via app.py to enable")
            create_user_btn.click(fb_user, inputs=[create_user_input], outputs=[gr.Textbox(visible=False), gr.Textbox(visible=False), gr.Textbox(visible=False), user_log])
            rename_user_btn.click(fb_user, inputs=[rename_user_input], outputs=[gr.Textbox(visible=False), gr.Textbox(visible=False), gr.Textbox(visible=False), user_log])
            delete_user_btn.click(lambda x: (gr.update(), gr.update(), gr.update(), "⚠️ Run via app.py to enable"), outputs=[gr.State(), gr.State(), gr.State(), delete_user_log])
            
            fb_proj = lambda x: (gr.update(), gr.update(), "⚠️ Run via app.py to enable")
            create_btn.click(fb_proj, inputs=[create_name_input], outputs=[gr.Textbox(visible=False), gr.Textbox(visible=False), project_log])
            rename_btn.click(fb_proj, inputs=[rename_name_input], outputs=[gr.Textbox(visible=False), gr.Textbox(visible=False), project_log])
            delete_btn.click(lambda x: (gr.update(), gr.update(), "⚠️ Run via app.py to enable"), outputs=[gr.State(), gr.State(), delete_log])


            
        refresh_btn.click(get_static_and_project_info, outputs=info_outputs)
        demo.load(get_static_and_project_info, outputs=info_outputs)

    return demo