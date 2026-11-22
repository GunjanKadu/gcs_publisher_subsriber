# Google Cloud Build Setup Guide

## Pub/Sub Publisher + Dataflow to BigQuery

This guide walks you through configuring Google Cloud using the UI and deploying your pipeline with Cloud Build.

---

## 📋 Overview

**What this does:**

1. Python script generates dummy messages → Pub/Sub
2. Cloud Build triggers deployment automatically
3. Dataflow pipeline processes messages → BigQuery

---

## 🎯 Part 1: GCP UI Configuration (One-Time Setup)

### Step 1: Create a New Project (if needed)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the project dropdown (top bar)
3. Click **"New Project"**
4. Enter project name (e.g., `data-pipeline-demo`)
5. Click **"Create"**
6. **Note your Project ID** (you'll need this!)

---

### Step 2: Enable Required APIs

1. Go to **APIs & Services** → **Library**
2. Search and enable each of these APIs:
   - ✅ **Cloud Build API**
   - ✅ **Pub/Sub API**
   - ✅ **Dataflow API**
   - ✅ **BigQuery API**
   - ✅ **Cloud Storage API**
   - ✅ **Compute Engine API**

_Or use the enable button that appears when visiting each service_

---

### Step 3: Create Pub/Sub Topic

1. Navigate to **Pub/Sub** → **Topics**
2. Click **"Create Topic"**
3. Topic ID: `data-ingestion-topic`
4. Leave defaults, click **"Create"**

---

### Step 4: Create Pub/Sub Subscription

1. In **Pub/Sub** → **Subscriptions**
2. Click **"Create Subscription"**
3. Subscription ID: `data-ingestion-subscription`
4. Select topic: `data-ingestion-topic`
5. Delivery type: **Pull**
6. Acknowledgment deadline: **60 seconds**
7. Click **"Create"**

---

### Step 5: Create BigQuery Dataset

1. Navigate to **BigQuery** → **SQL Workspace**
2. Click your project name in the Explorer
3. Click **⋮** (three dots) → **Create dataset**
4. Dataset ID: `event_data`
5. Location: `US (multi-region)` or choose your region
6. Click **"Create Dataset"**

_Note: Table will be created automatically by Dataflow_

---

### Step 6: Set Up Service Account Permissions

1. Go to **IAM & Admin** → **IAM**
2. Find the **Cloud Build service account**:
   - Format: `PROJECT-NUMBER@cloudbuild.gserviceaccount.com`
3. Click the **Edit** (pencil icon)
4. Click **"Add Another Role"** and add:
   - ✅ **Pub/Sub Publisher**
   - ✅ **Dataflow Admin**
   - ✅ **Dataflow Worker**
   - ✅ **BigQuery Data Editor**
5. Click **"Save"\*\***

---

## 🚀 Part 2: Deploy with Cloud Build

### Step 1: Prepare Your Code

1. **Update `cloudbuild.yaml`** with your project details:

   ```yaml
   substitutions:
     _PROJECT_ID: "your-project-id" # ← CHANGE THIS
     _REGION: "us-central1" # ← CHANGE IF NEEDED
   ```

2. **Update `publisher/publish_messages.py`** (Optional):
   - Modify `USER_IDS`, `EVENT_TYPES` arrays for different dummy data
   - Adjust message generation logic in `generate_dummy_message()`

---

### Step 2: Install gcloud CLI (if not installed)

**macOS:**

```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Initialize:**

```bash
gcloud init
gcloud auth login
gcloud config set project YOUR-PROJECT-ID
```

---

### Step 3: Submit Build Manually

Navigate to your project directory:

```bash
cd /path/to/your/project/pythonScript
```

Submit the build:

```bash
gcloud builds submit --config=cloudbuild.yaml .
```

**What happens:**

1. ✅ Installs Python dependencies
2. ✅ Runs publisher script (sends 5 dummy messages to Pub/Sub)
3. ✅ Deploys Dataflow pipeline
4. ✅ Dataflow starts processing messages → BigQuery

---

### Step 4: Monitor the Build

**View in Console:**

1. Go to **Cloud Build** → **History**
2. Click on the latest build
3. Watch real-time logs for each step

**View in CLI:**

```bash
gcloud builds list --limit=5
```

---

## 📊 Part 3: Verify Deployment

### Check Messages in Pub/Sub

1. Go to **Pub/Sub** → **Topics** → `data-ingestion-topic`
2. Click **"Messages"** tab
3. You should see published messages (if any are queued)

---

### Check Dataflow Pipeline

1. Go to **Dataflow** → **Jobs**
2. You should see a running job: `pubsub-to-bigquery-YYYYMMDD-HHMMSS`
3. Click on it to see:
   - Pipeline graph
   - Worker logs
   - Throughput metrics

⏱️ **Note:** Pipeline takes 5-10 minutes to fully start

---

### Check Data in BigQuery

1. Go to **BigQuery** → **SQL Workspace**
2. Navigate to: `event_data` → `events`
3. Click **"Preview"** or run:

```sql
SELECT *
FROM `your-project-id.event_data.events`
ORDER BY processed_at DESC
LIMIT 10
```

You should see your dummy messages!

---

## 🔄 Part 4: Automatic Deployment with Triggers

### Option A: Manual Trigger from UI

1. Go to **Cloud Build** → **Triggers**
2. Click **"Create Trigger"**
3. Name: `deploy-pipeline`
4. Event: **Manual invocation**
5. Source: **Inline**
6. Configuration type: **Cloud Build configuration file**
7. Location: `cloudbuild.yaml`
8. Click **"Create"**

**To run:** Click **"Run"** next to your trigger

---

### Option B: Git Integration (Advanced)

1. Push your code to GitHub or Cloud Source Repositories
2. In **Cloud Build** → **Triggers** → **Create Trigger**
3. Select repository
4. Branch: `main` (or your branch)
5. Configuration: `cloudbuild.yaml`
6. Click **"Create"**

**Now:** Every push to `main` auto-deploys!

---

## 🧪 Testing

### Send More Messages

Run the publisher locally:

```bash
cd publisher
pip install -r requirements.txt

export GCP_PROJECT="your-project-id"
export PUBSUB_TOPIC="data-ingestion-topic"
export NUM_MESSAGES=20

python publish_messages.py
```

---

### Query BigQuery

**Count by event type:**

```sql
SELECT event_type, COUNT(*) as count
FROM `your-project-id.event_data.events`
GROUP BY event_type
ORDER BY count DESC
```

**Average value per user:**

```sql
SELECT user_id, AVG(value) as avg_value, COUNT(*) as event_count
FROM `your-project-id.event_data.events`
GROUP BY user_id
ORDER BY avg_value DESC
```

---

## 📝 Cloud Build Configuration Explained

### `cloudbuild.yaml` Structure:

```yaml
substitutions:
  _PROJECT_ID: "your-project-id" # Variables
  _REGION: "us-central1"

steps:
  # Step 1: Install publisher dependencies
  - name: "python:3.11"
    id: "install-publisher-deps"
    entrypoint: "pip"
    args: ["install", "-r", "publisher/requirements.txt"]

  # Step 2: Run publisher
  - name: "python:3.11"
    id: "publish-messages"
    entrypoint: "python"
    args: ["publisher/publish_messages.py"]
    env:
      - "GCP_PROJECT=${_PROJECT_ID}"
      - "NUM_MESSAGES=5"
    waitFor: ["install-publisher-deps"] # Wait for step 1

  # Step 3: Deploy Dataflow
  - name: "python:3.11"
    id: "deploy-dataflow"
    entrypoint: "python"
    args: ["dataflow_pipeline/dataflow_pubsub_to_bigquery.py", ...]
```

**Key concepts:**

- `substitutions`: Variables you can override
- `steps`: Sequential build operations
- `waitFor`: Dependencies between steps
- `env`: Environment variables per step

---

## 🛠️ Customization

### Change Number of Messages

In `cloudbuild.yaml`, modify:

```yaml
env:
  - "NUM_MESSAGES=100" # ← Change this
  - "DELAY_SECONDS=0.5" # ← Delay between messages
```

### Modify Dummy Data

Edit `publisher/publish_messages.py`:

```python
USER_IDS = ['alice', 'bob', 'charlie']  # Your users
EVENT_TYPES = ['login', 'click', 'view']  # Your events

def generate_dummy_message():
    return {
        'user_id': random.choice(USER_IDS),
        'event_type': random.choice(EVENT_TYPES),
        'custom_field': 'your_value',  # Add custom fields
        # ...
    }
```

---

## 💰 Cost Management

### View Costs

1. Go to **Billing** → **Reports**
2. Filter by service:
   - Cloud Build
   - Dataflow
   - Pub/Sub
   - BigQuery

### Stop Dataflow Job

**Via UI:**

1. Go to **Dataflow** → **Jobs**
2. Click your job
3. Click **"Stop"**
4. Select **"Cancel"** or **"Drain"**

**Via CLI:**

```bash
gcloud dataflow jobs cancel JOB_ID --region=us-central1
```

---

## 🐛 Troubleshooting

### Build Fails: Permission Denied

**Solution:** Check service account permissions (Part 1, Step 7)

### No Data in BigQuery

**Check:**

1. Is Dataflow job running? (Dataflow → Jobs)
2. Are messages in Pub/Sub? (Pub/Sub → Subscriptions → View Messages)
3. Check Dataflow worker logs for errors

### Dataflow Job Fails

**Common issues:**

- Wrong Python version (use 3.11)
- Missing dependencies in `requirements.txt`
- Incorrect subscription format (should be `projects/PROJECT/subscriptions/NAME`)

**View logs:**

```bash
gcloud dataflow jobs list --region=us-central1
gcloud dataflow jobs show JOB_ID --region=us-central1
```

---

## 🧹 Cleanup

### Delete All Resources via UI

1. **Dataflow:** Stop all jobs
2. **Pub/Sub:** Delete subscription → Delete topic
3. **BigQuery:** Delete dataset `event_data`
4. **Cloud Build:** Delete triggers

---

## 📚 Next Steps

1. **Add authentication:** Secure your Cloud Build triggers
2. **Add monitoring:** Set up alerts for failed builds
3. **Create dashboard:** Visualize BigQuery data with Looker Studio
4. **Scale up:** Increase message volume and test performance
5. **Add tests:** Create unit tests for your pipeline

---

## 🎯 Quick Reference

| Service     | Resource                      | Purpose                  |
| ----------- | ----------------------------- | ------------------------ |
| Pub/Sub     | `data-ingestion-topic`        | Receives messages        |
| Pub/Sub     | `data-ingestion-subscription` | Dataflow reads from here |
| BigQuery    | `event_data.events`           | Stores processed data    |
| Cloud Build | `cloudbuild.yaml`             | Deployment configuration |

---

**You're all set! 🚀** Run `gcloud builds submit` whenever you want to deploy!
