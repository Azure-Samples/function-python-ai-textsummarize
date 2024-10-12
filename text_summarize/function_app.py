import azure.functions as func
import logging
from azure.ai.textanalytics import TextAnalyticsClient
from azure.identity import DefaultAzureCredential
import os

app = func.FunctionApp()

# Load AI url and secrets from Env Variables in Terminal before running, 
# e.g. `export TEXT_ANALYTICS_ENDPOINT=https://<your subdomain>.cognitiveservices.azure.com/`
endpoint = os.getenv('TEXT_ANALYTICS_ENDPOINT', 'SETENVVAR!') 

# Create client using Entra User or Managed Identity (no longer AzureKeyCredential)
# This requires a sub domain name to be set in endpoint URL for Managed Identity support
# See https://learn.microsoft.com/en-us/azure/ai-services/authentication#authenticate-with-microsoft-entra-id 
text_analytics_client = TextAnalyticsClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

@app.function_name(name="summarize_function")
@app.blob_trigger(arg_name="myblob", path="unprocessed-text/{name}",
                  connection="blobstorage")
@app.blob_output(arg_name="outputblob", path="processed-text/{name}-output.txt", connection="blobstorage")
def test_function(myblob: func.InputStream, outputblob: func.Out[str]):
   logging.info(f"Triggered item: {myblob.name}\n")

   document = [myblob.read().decode('utf-8')]
   summarized_text = ai_summarize_txt(document)
   logging.info(f"\n *****Summary***** \n{summarized_text}");
   outputblob.set(summarized_text)

# Example method for summarizing text
def ai_summarize_txt(document):

    poller = text_analytics_client.begin_extract_summary(document)
    extract_summary_results = poller.result()

    summarized_text = ""
    document_results = poller.result()
    for result in extract_summary_results:
        if result.kind == "ExtractiveSummarization":
            summarized_text= "Summary extracted: \n{}".format(
                " ".join([sentence.text for sentence in result.sentences]))
            print(summarized_text)
            logging.info(f"Returning summarized text:  \n{summarized_text}")
        elif result.is_error is True:
            print("...Is an error with code '{}' and message '{}'".format(
                result.error.code, result.error.message
            ))
            logging.error(f"Error with code '{result.error.code}' and message '{result.error.message}'")
