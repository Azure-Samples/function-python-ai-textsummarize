---
page_type: sample
languages:
- azdeveloper
- python
- bicep
products:
- azure
- azure-functions
- ai-services
- azure-cognitive-search
urlFragment: function-python-ai-textsummarize
name: Azure Functions - Text Summarization using AI Cognitive Language Service (Python v2 Function)
description: This sample shows how to take text documents as a input via BlobTrigger, does Text Summarization & Sentiment Score processing using the AI Congnitive Language service, and then outputs to another text document using BlobOutput binding. Deploys to Flex Consumption hosting plan of Azure Functions.  
---
<!-- YAML front-matter schema: https://review.learn.microsoft.com/en-us/help/contribute/samples/process/onboarding?branch=main#supported-metadata-fields-for-readmemd -->

# Azure Functions
## Text Summarization using AI Cognitive Language Service (Python v2 Function)

This sample shows how to take text documents as a input via BlobTrigger, does Text Summarization & Sentiment Score processing using the AI Congnitive Language service, and then outputs to another text document using BlobOutput binding. Deploys to Flex Consumption hosting plan of Azure Functions.  

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure-Samples/function-python-ai-textsummarize)

## Run on your local environment

### Pre-reqs
1) [Python 3.8+](https://www.python.org/) required 
2) [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=v4%2Cmacos%2Ccsharp%2Cportal%2Cbash#install-the-azure-functions-core-tools)
3) [Azurite](https://github.com/Azure/Azurite)

The easiest way to install Azurite is using a Docker container or the support built into Visual Studio:
```bash
docker run -d -p 10000:10000 -p 10001:10001 -p 10002:10002 mcr.microsoft.com/azure-storage/azurite
```

4) Once you have your Azure subscription, run the following in a new terminal window to create all the AI Language and other resources needed:
```bash
azd provision
```

Take note of the value of `TEXT_ANALYTICS_ENDPOINT` which can be found in `./.azure/<env name from azd provision>/.env`.  It will look something like:
```bash
TEXT_ANALYTICS_ENDPOINT="https://<unique string>.cognitiveservices.azure.com/"
```

Alternatively you can [create a Language resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics) in the Azure portal to get your key and endpoint. After it deploys, click Go to resource and view the Endpoint value.

5) [Azure Storage Explorer](https://azure.microsoft.com/en-us/products/storage/storage-explorer/) or storage explorer features of [Azure Portal](https://portal.azure.com)
6) Add this `local.settings.json` file to the `./text_summarization` folder to simplify local development.  Optionally fill in the AI_URL and AI_SECRET values per step 4.  This file will be gitignored to protect secrets from committing to your repo.  
```json
{
    "IsEncrypted": false,
    "Values": {
        "AzureWebJobsStorage": "UseDevelopmentStorage=true",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "TEXT_ANALYTICS_ENDPOINT": "<insert from step 4>"
    }
}
```

### Using VS Code
1) Open the root folder in VS Code:

```bash
code .
```
2) Ensure `local.settings.json` exists already using steps above
3) Run and Debug by pressing `F5`
4) Open Storage Explorer, Storage Accounts -> Emulator -> Blob Containers -> and create a container `unprocessed-text` if it does not already exists
5) Copy any .txt document file with text into the `unprocessed-text` container
6) In the Azure extension of VS Code, open Azure:Workspace -> Local Project -> Functions -> `summarize_function`.  Right-click and Execute Function now.  At the command palette prompt, enter the path to the storage blob you just uploaded: `unprocessed-text/<your_text_filename.txt>`.  This will simulate an EventGrid trigger locally and your function will trigger and show output in the terminal.  

You will see AI analysis happen in the Terminal standard out.  The analysis will be saved in a .txt file in the `processed-text` blob container.

Note, this newer mechanism for BlobTrigger with EventGrid source is documented in more detail here: https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger?pivots=programming-language-python#run-the-function-locally. 

## Deploy to Azure

The easiest way to deploy this app is using the [Azure Developer CLI](https://aka.ms/azd).  If you open this repo in GitHub CodeSpaces the AZD tooling is already preinstalled.

To provision and deploy:
1) Open a new terminal and do the following from root folder:
```bash
azd up
```

## Understand the Code

The main operation of the code starts with the `summarize_function` function in [function_app.py](./text_summarize/function_app.py).  The function is triggered by a Blob uploaded event using BlobTrigger with EventGrid, your code runs to do the processing with AI, and then the output is returned as another blob file simply by returning a value and using the BlobOutput binding.  

```python
@app.function_name(name="summarize_function")
@app.blob_trigger(
    arg_name="myblob", path="unprocessed-text/{name}",
    connection="AzureWebJobsStorage",
    source="EventGrid"
    )
@app.blob_output(
    arg_name="outputblob", path="processed-text/{name}-output.txt",
    connection="AzureWebJobsStorage")
def test_function(myblob: func.InputStream, outputblob: func.Out[str]):
    logging.info(f"Triggered item: {myblob.name}\n")

    document = [myblob.read().decode('utf-8')]
    summarized_text = ai_summarize_txt(document)
    logging.info(f"\n *****Summary***** \n{summarized_text}")
    outputblob.set(summarized_text)
```

The `ai_summarize_txt` helper function does the heavy lifting for summary extraction and sentiment analysis using the `TextAnalyticsClient` SDK from the [AI Language Services](https://learn.microsoft.com/en-us/azure/ai-services/language-service/):

```python


# Example method for summarizing text
def ai_summarize_txt(document):

    poller = text_analytics_client.begin_extract_summary(document)
    extract_summary_results = poller.result()
    summarized_text = ""

    for result in extract_summary_results:
        if result.kind == "ExtractiveSummarization":
            summarized_text = "Summary extracted: \n{}".format(
                " ".join([sentence.text for sentence in result.sentences]))
            print(summarized_text)
            logging.info(f"Returning summarized text:  \n{summarized_text}")
        elif result.is_error is True:
            print("...Is an error with code '{}' and message '{}'".format(
                result.error.code, result.error.message
            ))
            logging.error(
                f"Error with code '{result.error.code}' and message " +
                "'{result.error.message}'"
            )

    # Perform sentiment analysis on document summary
    sentiment_result = text_analytics_client.analyze_sentiment(
        [summarized_text]
        )[0]
    print(f"\nSentiment: {sentiment_result.sentiment}")
    print(f"Positive Score: {sentiment_result.confidence_scores.positive}")
    print(f"Negative Score: {sentiment_result.confidence_scores.negative}")
    print(f"Neutral Score: {sentiment_result.confidence_scores.neutral}")

    summary_with_sentiment = (
        summarized_text + "\nSentiment: " + f"{sentiment_result.sentiment}\n"
    )

    return summary_with_sentiment
```
