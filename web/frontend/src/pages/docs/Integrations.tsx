export default function Integrations() {
  return (
    <div className="docs-content">
      <h1>Integrations</h1>

      <p>
        Company Eval can send notifications to Slack or Microsoft Teams when evaluation runs
        complete. This helps your team stay informed about quality regressions without
        constantly checking the dashboard.
      </p>

      <h2>Setting Up Notifications</h2>

      <p>
        To configure notifications, go to the <strong>Dashboard</strong> and scroll down to
        the <strong>Integrations</strong> section. Click <strong>Add Integration</strong> to
        get started.
      </p>

      <h3>Slack Setup</h3>

      <ol>
        <li>
          <strong>Create a Slack App:</strong> Go to{' '}
          <a href="https://api.slack.com/apps" target="_blank" rel="noopener noreferrer">
            api.slack.com/apps
          </a>{' '}
          and click "Create New App"
        </li>
        <li>
          <strong>Choose "From scratch"</strong> and give your app a name (e.g., "Company Eval Notifications")
        </li>
        <li>
          <strong>Enable Incoming Webhooks:</strong> In your app settings, go to "Incoming Webhooks"
          and toggle it on
        </li>
        <li>
          <strong>Add a Webhook:</strong> Click "Add New Webhook to Workspace" and select the
          channel where you want notifications
        </li>
        <li>
          <strong>Copy the Webhook URL:</strong> It will look like{' '}
          <code>https://hooks.slack.com/services/TXXXXX/BXXXXX/your-webhook-token</code>
        </li>
        <li>
          <strong>Paste in Dashboard:</strong> Add the webhook URL in the Company Eval Dashboard
          integrations section
        </li>
      </ol>

      <h3>Microsoft Teams Setup</h3>

      <ol>
        <li>
          <strong>Open Teams:</strong> Navigate to the channel where you want notifications
        </li>
        <li>
          <strong>Add Connector:</strong> Click the "..." menu on the channel and select "Connectors"
        </li>
        <li>
          <strong>Find Incoming Webhook:</strong> Search for "Incoming Webhook" and click "Configure"
        </li>
        <li>
          <strong>Name your webhook:</strong> Give it a name like "Company Eval" and optionally
          upload an icon
        </li>
        <li>
          <strong>Copy the Webhook URL:</strong> It will look like{' '}
          <code>https://outlook.office.com/webhook/...</code>
        </li>
        <li>
          <strong>Paste in Dashboard:</strong> Add the webhook URL in the Company Eval Dashboard
          integrations section
        </li>
      </ol>

      <h2>Notification Triggers</h2>

      <p>
        When configuring an integration, you can choose when to receive notifications:
      </p>

      <table>
        <thead>
          <tr>
            <th>Trigger</th>
            <th>Description</th>
            <th>Recommended For</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Evaluation fails</strong></td>
            <td>Send a notification when any eval run fails to meet thresholds</td>
            <td>All teams - catch regressions immediately</td>
          </tr>
          <tr>
            <td><strong>Evaluation passes</strong></td>
            <td>Send a notification when eval runs pass all thresholds</td>
            <td>Teams wanting full visibility into CI/CD</td>
          </tr>
        </tbody>
      </table>

      <p>
        Most teams enable <strong>failures only</strong> to avoid notification fatigue while
        still catching quality regressions.
      </p>

      <h2>Notification Format</h2>

      <p>
        When triggered, notifications include:
      </p>

      <ul>
        <li>App name and evaluation suite</li>
        <li>Pass/Fail status with color coding</li>
        <li>Metric scores and thresholds</li>
        <li>Git branch and commit (if available)</li>
        <li>Link to view full results in the dashboard</li>
      </ul>

      <h2>Managing Integrations</h2>

      <p>
        From the Dashboard integrations section, you can:
      </p>

      <ul>
        <li><strong>Toggle on/off:</strong> Temporarily disable notifications without deleting the config</li>
        <li><strong>Edit:</strong> Update the webhook URL or notification triggers</li>
        <li><strong>Delete:</strong> Permanently remove the integration</li>
      </ul>

      <h2>Troubleshooting</h2>

      <h3>Not receiving notifications?</h3>

      <ul>
        <li>Verify the webhook URL is correct and the integration is set to "Active"</li>
        <li>Check that at least one trigger (failures or passes) is enabled</li>
        <li>For Slack, ensure the app is still installed in your workspace</li>
        <li>For Teams, verify the connector is still configured on the channel</li>
      </ul>

      <h3>Getting too many notifications?</h3>

      <ul>
        <li>Consider enabling only "Evaluation fails" to reduce volume</li>
        <li>Use the toggle to temporarily disable during high-activity periods</li>
      </ul>
    </div>
  )
}
