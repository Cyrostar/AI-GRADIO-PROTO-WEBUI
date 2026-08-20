import gradio as gr
import os

from core import core
from core.core import _

def download_model_fn(model_id, filename=None, allow_patterns=None, revision=None):
    if not model_id or not model_id.strip():
        return "❌ Error: Model ID cannot be empty."
    
    clean_id = model_id.strip()
    clean_file = filename.strip() if filename else ""
    orig_transformers_offline = os.environ.get('TRANSFORMERS_OFFLINE', '0')
    orig_hf_offline = os.environ.get('HF_HUB_OFFLINE', '0')
    orig_hf_transfer = os.environ.get('HF_HUB_ENABLE_HF_TRANSFER', '0')
    
    # Temporarily set offline mode to False and disable hf_transfer
    os.environ['TRANSFORMERS_OFFLINE'] = '0'
    os.environ['HF_HUB_OFFLINE'] = '0'
    os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '0'
    
    try:
        import huggingface_hub.constants
        huggingface_hub.constants.HF_HUB_OFFLINE = False
        huggingface_hub.constants.HF_HUB_ENABLE_HF_TRANSFER = False
    except Exception:
        pass
        
    try:
        import transformers.utils.hub
        transformers.utils.hub._is_offline_mode = False
    except Exception:
        pass
    
    try:
        if clean_file:
            from huggingface_hub import hf_hub_download
            if revision:
                hf_hub_download(repo_id=clean_id, filename=clean_file, revision=revision)
            else:
                hf_hub_download(repo_id=clean_id, filename=clean_file)
            return f"✅ Successfully downloaded file: {clean_file} from {clean_id}"
        else:
            from huggingface_hub import snapshot_download
            if allow_patterns:
                snapshot_download(repo_id=clean_id, allow_patterns=allow_patterns)
            else:
                snapshot_download(repo_id=clean_id)
            return f"✅ Successfully downloaded model: {clean_id}"
    except Exception as e:
        return f"❌ Download failed: {str(e)}"
    finally:
        # Restore original settings
        os.environ['TRANSFORMERS_OFFLINE'] = orig_transformers_offline
        os.environ['HF_HUB_OFFLINE'] = orig_hf_offline
        os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = orig_hf_transfer
        
        try:
            import huggingface_hub.constants
            huggingface_hub.constants.HF_HUB_OFFLINE = (orig_hf_offline == '1' or orig_transformers_offline == '1')
            huggingface_hub.constants.HF_HUB_ENABLE_HF_TRANSFER = (orig_hf_transfer == '1')
        except Exception:
            pass
            
        try:
            import transformers.utils.hub
            transformers.utils.hub._is_offline_mode = (orig_hf_offline == '1' or orig_transformers_offline == '1')
        except Exception:
            pass

def get_downloaded_models_fn():
    cache_dir = os.environ.get("HF_HUB_CACHE")
    if not cache_dir:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cache_dir = os.path.join(base_dir, "models", "hf", "hf_cache")
        
    if not os.path.exists(cache_dir):
        return _("HOME_NO_MODELS")
        
    models = []
    try:
        for item in os.listdir(cache_dir):
            item_path = os.path.join(cache_dir, item)
            if os.path.isdir(item_path) and item.startswith("models--"):
                parts = item.split("--")
                if len(parts) >= 3:
                    author = parts[1]
                    model_name = "--".join(parts[2:])
                    repo_id = f"{author}/{model_name}"
                else:
                    repo_id = item
                
                # Check for files in snapshots
                snapshots_dir = os.path.join(item_path, "snapshots")
                files_list = []
                if os.path.exists(snapshots_dir):
                    try:
                        commits = os.listdir(snapshots_dir)
                        if commits:
                            commit_dir = os.path.join(snapshots_dir, commits[0])
                            if os.path.isdir(commit_dir):
                                files = [f for f in os.listdir(commit_dir) if os.path.isfile(os.path.join(commit_dir, f))]
                                if files:
                                    files_list = sorted(files)
                    except Exception:
                        pass
                
                model_str = f"📦 {repo_id}"
                if files_list:
                    file_lines = [f"   {idx+1}. 📄 {file}" for idx, file in enumerate(files_list)]
                    model_str += "\n" + "\n".join(file_lines)
                
                models.append(model_str)
    except Exception as e:
        return f"❌ Error: {str(e)}"
        
    if not models:
        return _("HOME_NO_MODELS")
        
    return "\n\n".join(models)

def create_models_tab():
    with gr.Column(scale=1, variant="panel"):
        # Model Download
        gr.Markdown(_("HOME_MODEL_DOWNLOAD"))
        with gr.Row():
            model_id_input = gr.Textbox(placeholder=_("HOME_PLACEHOLDER_MODEL_ID"), show_label=False, container=False, scale=1)
        with gr.Row():
            filename_input = gr.Textbox(placeholder=_("HOME_PLACEHOLDER_FILENAME"), show_label=False, container=False, scale=3)
            download_btn = gr.Button(_("HOME_BTN_DOWNLOAD"), variant="primary", scale=1)
        download_log = gr.Textbox(label=_("HOME_DOWNLOAD_STATUS"), lines=2, interactive=False)
        
        gr.HTML("<hr>")
        
        # Model List
        gr.Markdown(_("HOME_MODEL_LIST"))
        model_list_box = gr.Textbox(label=_("HOME_DOWNLOADED_MODELS"), lines=12, interactive=False)
        refresh_models_btn = gr.Button(_("HOME_BTN_REFRESH_MODELS"), variant="secondary")

    download_btn.click(
        download_model_fn, 
        inputs=[model_id_input, filename_input], 
        outputs=[download_log]
    ).success(
        get_downloaded_models_fn, 
        outputs=[model_list_box]
    )
    
    refresh_models_btn.click(
        get_downloaded_models_fn, 
        outputs=[model_list_box]
    )
    
    return model_list_box
