# Google Cloud Build Deployment Guide

## Python Publisher → Pub/Sub → Dataflow → BigQuery

Complete guide for deploying a data pipeline using Cloud Build automation.

---

## 🎯 What You'll Build

**Pipeline Flow:**

```
Python Script (dummy data) → Pub/Sub → Dataflow → BigQuery
                    ↑
            Cloud Build (automated)
```

**Key Features:**

- ✅ Automatic deployment with Cloud Build
- ✅ Dummy message generation
- ✅ Real-time data processing
- ✅ BigQuery analytics
- ✅ One-command deployment

---

## 📋 Part 1: GCP UI Configuration

### Step 1: Create/Select Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. **Note your Project ID** (e.g., `my-pipeline-project-123`)

---

### Step 2: Enable APIs

Navigate to **APIs & Services → Library** and enable:

- ✅ Cloud Build API
- ✅ Pub/Sub API
- ✅ Dataflow API
- ✅ BigQuery API
- ✅ Cloud Storage API
- ✅ Compute Engine API
- ✅ Cloud Source Repositories API

---

### Step 3: Create Cloud Source Repository

1. Go to **Cloud Source Repositories** in the console
2. Click **"Add repository"**
3. Select **"Create new repository"**
4. Repository name: `pubsub-publisher`
5. Project: Select your project (`de2-bigquery`)
6. Click **"Create"**
7. **Important**: After creation, you'll see instructions - keep this page open

**Push your code to the repository:**

```bash
# Navigate to your project directory
cd /path/to/your/project/pythonScript

# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Add Cloud Source Repository as remote
gcloud source repos clone pubsub-publisher --project=de2-bigquery

# Copy your files to the cloned repo
cp -r * pubsub-publisher/
cd pubsub-publisher

# Push to Cloud Source Repository
git add .
git commit -m "Add publisher code"
git push origin main
```

Or use the UI to upload files:

1. In the repository page, click **"Upload files"**
2. Select all your project files
3. Add commit message: `Initial commit`
4. Click **"Commit"**

---

### Step 4: Create BigQuery Dataset

1. Go to **BigQuery → SQL Workspace**
2. Click your project name
3. Click **⋮ → Create dataset**
4. Dataset ID: `event_data`
5. Location: **US** or your preferred region
6. Click **Create**

---

### Step 5: Configure Cloud Build Permissions

1. Go to **IAM & Admin → IAM**
2. Find: `PROJECT-NUMBER@cloudbuild.gserviceaccount.com`
3. Click **Edit** (pencil icon)
4. Add roles:
   - Pub/Sub Admin
   - Dataflow Admin
   - Dataflow Worker
   - BigQuery Data Editor
5. Click **Save**

---

## 🔨 Part 2: Create Cloud Build Trigger

### Step 1: Create the Trigger

1. Go to **Cloud Build → Triggers**
2. Click **"Create Trigger"**
3. Configure:
   - **Name**: `scheduled-publisher`
   - **Description**: `Automated publisher for Pub/Sub`
   - **Event**: Select **Pub/Sub message**
   - **Pub/Sub topic**:
     - Click **"Create a topic"**
     - Topic name: `build-scheduler-trigger`
     - Click **"Create topic"**
   - **Source**: Select **Cloud Source repository (1st gen)**
     - **Repository**: `pubsub-publisher`
     - **Branch**: `^main$`
   - **Configuration**:
     - Type: **Cloud Build configuration file (yaml or json)**
     - Location: `cloudbuild.yaml`
   - **Substitution variables** (click "Add variable" for each):
     - `_PROJECT_ID` = `de2-bigquery`
     - `_TOPIC_NAME` = `data-ingestion-topic`
     - `_SUBSCRIPTION_NAME` = `data-ingestion-subscription`
4. Click **"Create"**

---

### Step 2: Test the Trigger Manually

1. In **Cloud Build → Triggers**, find `scheduled-publisher`
2. Click **"Run"** (play button)
3. Click **"Run trigger"**
4. Go to **Cloud Build → History** to see the build running
5. Check logs to verify:
   - Topic created
   - Subscription created
   - Messages published

---

## ⏰ Part 3: Set Up Cloud Scheduler (Optional - For Automation)

### Create Scheduled Job

1. Go to **Cloud Scheduler** in the console
2. If first time: Click **"Create schedule"** and select region: `global`
3. Click **"Create Job"**
4. Configure:
   - **Name**: `publish-every-2min`
   - **Region**: `global`
   - **Description**: `Triggers Cloud Build every 2 minutes`
   - **Frequency**: `*/2 * * * *` (every 2 minutes)
   - **Timezone**: Select your timezone
5. Click **"Continue"**
6. Configure execution:
   - **Target type**: **Pub/Sub**
   - **Topic**: `build-scheduler-trigger`
   - **Message body**: `{"trigger":"scheduled-run"}`
7. Click **"Continue"**
8. Click **"Create"**

---

### Test the Scheduler

1. In **Cloud Scheduler**, find `publish-every-2min`
2. Click the job name
3. Click **"Force run"** at the top
4. Go to **Cloud Build → History** - you should see a new build!

---

### Manage the Scheduler

**Pause:**

1. Select the job checkbox
2. Click **"Pause"**

**Resume:**

1. Select the job
2. Click **"Resume"**

**Change frequency:**

1. Click the job name
2. Click **"Edit"** at the top
3. Change **Frequency** field:
   - `*/2 * * * *` = Every 2 minutes
   - `*/5 * * * *` = Every 5 minutes
   - `*/10 * * * *` = Every 10 minutes
   - `0 * * * *` = Every hour
4. Click **"Update"**

---

## 📊 Part 4: Verify Everything Works

### Check Pub/Sub Messages

1. Go to **Pub/Sub → Topics**
2. Click `data-ingestion-topic`
3. Click **"Messages"** tab
4. Click **"Pull"** to see published messages

---

### Check BigQuery Data (After setting up Dataflow)

Run this query in **BigQuery**:

```sql
SELECT *
FROM `de2-bigquery.event_data.events`
ORDER BY processed_at DESC
LIMIT 10
```

---

## 🛠️ Part 5: Set Up Dataflow (Manual via UI)

### BigQuery Table Schema

Before setting up Dataflow, ensure your BigQuery table has the correct schema:

**Schema (JSON format):**

```json
[
  { "name": "user_id", "type": "STRING", "mode": "REQUIRED" },
  { "name": "event_type", "type": "STRING", "mode": "REQUIRED" },
  { "name": "value", "type": "FLOAT", "mode": "NULLABLE" },
  { "name": "timestamp", "type": "TIMESTAMP", "mode": "NULLABLE" },
  { "name": "processed_at", "type": "TIMESTAMP", "mode": "NULLABLE" },
  { "name": "status", "type": "STRING", "mode": "NULLABLE" }
]
```

**Or create table via UI:**

| Field name   | Type      | Mode     |
| ------------ | --------- | -------- |
| user_id      | STRING    | REQUIRED |
| event_type   | STRING    | REQUIRED |
| value        | FLOAT     | NULLABLE |
| timestamp    | TIMESTAMP | NULLABLE |
| processed_at | TIMESTAMP | REQUIRED |
| status       | STRING    | REQUIRED |

---

### Create Dataflow Job from Template

1. Go to **Dataflow → Create Job from Template**
2. Configure:
   - **Job name**: `pubsub-to-bigquery`
   - **Regional endpoint**: `us-central1`
   - **Dataflow template**: **Pub/Sub to BigQuery**
3. Required parameters:
   - **Input Pub/Sub subscription**: `projects/de2-bigquery/subscriptions/data-ingestion-subscription`
   - **BigQuery output table**: `de2-bigquery:event_data.events`
4. Optional parameters:
   - Leave defaults
5. Click **"Run job"**
6. Wait 5-10 minutes for workers to start

---

## 📝 Manual Deployment (Alternative to Scheduler)

If you prefer to trigger builds manually instead of scheduling:

```bash
# Navigate to project
cd /path/to/your/project/pythonScript

# Login
gcloud auth login
gcloud config set project de2-bigquery

# Deploy
gcloud builds submit --config=cloudbuild.yaml .
```

---

## 🧪 Customization & Testing

### Customize Message Generation

Edit `publisher/publish_messages.py` in your Cloud Source Repository:

```python
# Change these arrays
USER_IDS = ['alice', 'bob', 'charlie']
EVENT_TYPES = ['login', 'purchase', 'view']

# Modify message structure
def generate_dummy_message():
    return {
        'user_id': random.choice(USER_IDS),
        'event_type': random.choice(EVENT_TYPES),
        'value': round(random.uniform(0, 100), 2),
        'custom_field': 'your_data',  # Add fields
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
```

**After editing:**

1. Commit changes in Cloud Source Repository
2. Trigger will automatically use the updated code

### Change Number of Messages

Edit `cloudbuild.yaml` substitutions or environment variables:

```yaml
env:
  - "NUM_MESSAGES=10" # Change from 5 to 10
  - "DELAY_SECONDS=2" # Change delay between messages
```

---

        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

````

---

## 📝 Files Explained

### 1. `cloudbuild.yaml`

Cloud Build configuration with deployment steps:

- Install dependencies
- Run publisher
- Deploy Dataflow

### 2. `publisher/publish_messages.py`

Python script that:

- Generates dummy messages
- Publishes to Pub/Sub
- Configurable via environment variables

### 3. `dataflow_pipeline/dataflow_pubsub_to_bigquery.py`

Apache Beam pipeline that:

- Reads from Pub/Sub
- Parses JSON
- Transforms data
- Writes to BigQuery

---

## 🛠️ Troubleshooting

### Build Fails: Permission Denied

**Fix:** Check service account roles (Part 1, Step 6)

### No Data in BigQuery

**Check:**

1. Is Dataflow job running?
2. View Dataflow logs for errors
3. Check Pub/Sub subscription for undelivered messages

### Dataflow Startup Slow

**Normal:** Takes 5-10 minutes to provision workers

---

## 💰 Cost Management

### View Costs

- Go to **Billing → Reports**
- Filter by: Cloud Build, Dataflow, Pub/Sub

### Stop Services

```bash
# Stop Dataflow
gcloud dataflow jobs cancel JOB_ID --region=us-central1

# Or via UI: Dataflow → Jobs → Stop
````

---

## 🧹 Cleanup

**Delete all resources:**

```bash
# Stop Dataflow
gcloud dataflow jobs cancel $(gcloud dataflow jobs list --region=us-central1 --status=active --format="value(id)") --region=us-central1

# Delete Pub/Sub
gcloud pubsub subscriptions delete data-ingestion-subscription
gcloud pubsub topics delete data-ingestion-topic

# Delete BigQuery dataset
bq rm -r -f -d event_data
```

---

## 📚 Resources

- [Cloud Build Docs](https://cloud.google.com/build/docs)
- [Dataflow Docs](https://cloud.google.com/dataflow/docs)
- [Apache Beam Python SDK](https://beam.apache.org/documentation/sdks/python/)

---

## 🎯 Quick Reference

| File                            | Purpose             |
| ------------------------------- | ------------------- |
| `cloudbuild.yaml`               | Build configuration |
| `publisher/publish_messages.py` | Message generator   |
| `dataflow_pipeline/*.py`        | Processing pipeline |
| `.gcloudignore`                 | Files to exclude    |

**Deploy command:**

```bash
gcloud builds submit --config=cloudbuild.yaml .
```

---

**Happy building! 🚀**
