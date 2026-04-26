# Meta WhatsApp API Connection Guide

Follow these steps to connect your agent to the WhatsApp Business Platform.

## 1. Create a Meta Developer App
1.  Go to the [Meta for Developers](https://developers.facebook.com/) portal.
2.  Click **My Apps** > **Create App**.
3.  Select **Other** > **Business**.
4.  Give your app a name and click **Create App**.

## 2. Add WhatsApp to your App
1.  In your App Dashboard, scroll down to **WhatsApp** and click **Set up**.
2.  Select or create a **Meta Business Account**.

## 3. Get your IDs and Temporary Token
1.  Go to **WhatsApp** > **API Setup** in the left sidebar.
2.  Note your **Phone Number ID** (used in `src/api/outbound.py`).
3.  Note your **WhatsApp Business Account ID**.
4.  Copy the **Temporary Access Token** for initial testing (expires in 24 hours).

## 4. Configure Webhooks
1.  Go to **WhatsApp** > **Configuration**.
2.  Click **Edit** next to Callback URL.
3.  **Callback URL:** `https://your-ngrok-url.ngrok-free.app/webhook`
4.  **Verify Token:** The string you set as `META_VERIFY_TOKEN` in your `.env`.
5.  Click **Verify and Save**.
6.  Under **Webhook Fields**, click **Manage** and subscribe to **messages**.

## 5. Get a Permanent Token (Production)
Temporary tokens expire. For production:
1.  Go to your [Meta Business Suite Settings](https://business.facebook.com/settings/).
2.  Select **Users** > **System Users**.
3.  Add a new system user and assign it the **Admin** role.
4.  Click **Generate New Token**.
5.  Select your App and check the **whatsapp_business_messaging** and **whatsapp_business_management** permissions.
6.  Copy this token to your `.env` as `META_ACCESS_TOKEN`.
