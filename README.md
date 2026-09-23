# Sphelele

A mobile-friendly beauty booking platform for Sphelele.

## Run locally

No installation or build step is required.

1. Open a terminal in this folder.
2. Run one of the following commands:

```bash
python -m http.server 5500
```

or, if Node.js is installed:

```bash
npx serve .
```

3. Open http://localhost:5500 in your browser.

You can also open `index.html` directly, but a local server is recommended for a realistic client demo.

## Included in this demo

- Short client flow: service, date/time, optional note, and contact details
- Unavailable states for booked and lunch slots
- Deposit summary and paid booking confirmation state
- Admin starts empty and only shows bookings after payment confirmation
- Block-time modal for personal time or business breaks
- Responsive layout for phone and desktop
- WhatsApp-only confirmations and reminder-ready booking details
- Studio hours: Monday to Sunday, 08:00–19:00

## Deploy to Render

This project is configured as a Render Static Site. Push this folder to a GitHub or GitLab repository, then in Render choose **New > Blueprint** and select the repository. Render will read `render.yaml`, publish the project root, and deploy `index.html` without a build command.

You can also choose **New > Static Site** manually with:

- Build command: leave empty
- Publish directory: `.`
- Auto-deploy: enabled

After deployment, Render provides a public `onrender.com` URL. Add the custom domain from the Render settings when the client is ready.

## Production handoff

This is a front-end prototype. It is ready to use as a clickable client demo, but a static website cannot securely confirm payments or send automatic WhatsApp messages by itself. WhatsApp is the only notification channel in the client flow. To launch it for a client:

1. Replace the sample WhatsApp number in `index.html`.
2. Move services, working hours, blocked times, clients, and appointments into Django models.
3. Use a transaction plus database constraint to prevent overlapping appointments.
4. Replace the payment confirmation demo in `script.js` with PayFast, Peach Payments, Yoco, or another South African provider. Never store card details in this app.
5. Add a scheduled Django task/Celery job for 24-hour and 2-hour reminders through the WhatsApp Business Cloud API or a provider such as Twilio. The provider's access token must stay server-side.
6. Add owner authentication and permissions around the dashboard.
7. Deploy the Django API separately, update the front end API URL, then connect a custom domain.

The current interface is intentionally demo-ready without a build dependency, so it can be shown to the client before backend work begins.
