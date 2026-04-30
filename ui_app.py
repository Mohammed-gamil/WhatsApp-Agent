import streamlit as st
import requests
import json
import time
from app.config import settings

st.set_page_config(page_title="WhatsApp AI Agent Admin", page_icon="🤖")

st.title("🤖 WhatsApp AI Agent Control Center")

# Sidebar - Settings & Status
st.sidebar.header("System Status")
try:
    # Check if local FastAPI server is running
    res = requests.get("http://localhost:8080/", timeout=2)
    if res.status_code == 200:
        st.sidebar.success("FastAPI Server: ONLINE")
    else:
        st.sidebar.error("FastAPI Server: OFFLINE")
except:
    st.sidebar.error("FastAPI Server: OFFLINE")

st.sidebar.info(f"Model: {settings.llm_model}")

# Webhook Configuration
st.sidebar.markdown("---")
st.sidebar.header("🌐 Webhook Settings")
ngrok_url = st.sidebar.text_input("Ngrok Base URL", placeholder="https://xxxx.ngrok-free.app")
if st.sidebar.button("Update Webhook"):
    if not ngrok_url:
        st.sidebar.error("Please enter a URL")
    else:
        # Check if the path is already appended
        target_path = "/api/v1/webhook/whats360"
        clean_url = ngrok_url.rstrip('/')
        if target_path in clean_url:
            full_webhook_url = clean_url
        else:
            full_webhook_url = f"{clean_url}{target_path}"
        
        try:
            res = requests.post(
                "http://localhost:8080/api/v1/config/webhook",
                json={"url": full_webhook_url}
            )
            if res.status_code == 200:
                st.sidebar.success("Webhook updated in Whats360!")
            else:
                st.sidebar.error(f"Failed: {res.status_code}")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# Tabs for different functions
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat Simulator", "📢 Campaign Manager", "⚙️ Logs", "⚙️ Settings"])

with tab1:
    st.header("Test Chat Interface")
    st.write("Use this to simulate an incoming WhatsApp message.")
    
    with st.form("chat_form"):
        phone = st.text_input("Sender Phone Number", value="201097294152")
        message = st.text_area("User Message", placeholder="Type a message to the AI...")
        submit = st.form_submit_button("Send to Webhook")
        
        if submit:
            if not message:
                st.warning("Please enter a message.")
            else:
                # Wrap payload in Whats360 v2 event format
                wrapped_payload = {
                    "event": "message.received",
                    "data": {
                        "from": phone, 
                        "text": message,
                        "message_id": f"test_{int(time.time())}",
                        "instance_id": settings.whats360_instance_id,
                        "sender_name": "UI Tester"
                    }
                }
                try:
                    response = requests.post(
                        "http://localhost:8080/api/v1/webhook/whats360",
                        json=wrapped_payload
                    )
                    if response.status_code == 200:
                        st.success("Message sent to webhook successfully!")
                        st.json(response.json())
                    else:
                        st.error(f"Error: {response.status_code}")
                        st.write(response.text)
                except Exception as e:
                    st.error(f"Connection Error: {e}")

with tab2:
    st.header("Bulk Campaign Control")
    st.write("Directly trigger a campaign via the API.")
    
    campaign_name = st.text_input("Campaign Name")
    campaign_msg = st.text_area("Campaign Message")
    recipients_raw = st.text_area("Recipients (JSON list)", value='[{"phone": "2010...", "name": "User"}]')
    
    if st.button("Launch Campaign"):
        st.warning("Manual campaign triggering from UI coming soon. For now, the AI can trigger this via Chat.")

with tab3:
    st.header("Live Terminal Output")
    st.write("Check your terminal/console where you ran `run.cmd` for real-time logs.")
    st.code("tail -f app.log", language="bash")

with tab4:
    st.header("Agent Configuration")
    
    # Fetch current config
    try:
        config_res = requests.get("http://localhost:8080/api/v1/config", timeout=5)
        if config_res.status_code == 200:
            config = config_res.json()
            
            # 1. LLM Settings
            st.subheader("LLM Settings")
            provider = st.selectbox("Provider", ["openrouter", "openai", "groq"], index=0)
            model_name = st.text_input("Model Name", value=config["llm"]["model"])
            temp = st.slider("Temperature", 0.0, 1.0, float(config["llm"]["temperature"]), 0.1)
            
            # 2. System Prompt
            st.subheader("System Prompt")
            prompt = st.text_area("Base Instructions", value=config["system_prompt"], height=200)
            
            # 3. Tools Toggles
            st.subheader("Enabled Tools")
            t_text = st.checkbox("Text Messaging", value=config["tools_enabled"]["send_whatsapp_text"])
            t_image = st.checkbox("Image Support", value=config["tools_enabled"]["send_whatsapp_image"])
            t_doc = st.checkbox("Document Support", value=config["tools_enabled"]["send_whatsapp_document"])
            t_camp = st.checkbox("Campaign Management", value=config["tools_enabled"]["launch_whatsapp_campaign"])
            
            if st.button("Save Settings"):
                updated_config = {
                    "system_prompt": prompt,
                    "llm": {"provider": provider, "model": model_name, "temperature": temp},
                    "tools_enabled": {
                        "send_whatsapp_text": t_text,
                        "send_whatsapp_image": t_image,
                        "send_whatsapp_document": t_doc,
                        "launch_whatsapp_campaign": t_camp
                    },
                    "rag": config.get("rag", {"enabled": False, "backend_url": ""})
                }
                save_res = requests.post("http://localhost:8080/api/v1/config", json=updated_config)
                if save_res.status_code == 200:
                    st.success("Configuration updated successfully!")
                else:
                    st.error(f"Failed to update configuration: {save_res.status_code}")
        else:
            st.error(f"Could not fetch configuration from backend. Status: {config_res.status_code}")
    except Exception as e:
        st.error(f"Connection Error: {e}. Is the FastAPI server running?")
