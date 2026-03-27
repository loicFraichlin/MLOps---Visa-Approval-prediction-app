# MLOps---Visa-Approval-prediction-app

- Anaconda : https://www.anaconda.com/
- Vs code: https://code.visualstudio.com/download
- Flowchart: https://whismsical.com/
- MLOps Tools: https://evidentlyai.com
- Dataset link: https://www.kaggle.com/datasets/moro23/easyvisa-dataset



## Create virtual environment

```bash
conda create -n visa python=3.8 -y
```

```bash
conda activate visa
```

```bash
pip install -r requirements.txt
```

### Export the  environment variable
```bash


export MONGODB_URL="mongodb+srv://<username>:<password>...."

export AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>

export AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>


```

## Workflow:

1. constants
2. entity
3. components
4. pipeline
5. Main file