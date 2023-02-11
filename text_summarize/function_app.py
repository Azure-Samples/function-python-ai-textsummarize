import azure.functions as func
import logging
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import os

app = func.FunctionApp()

# Load AI url and secrets from Env Variables in Terminal before running, 
# e.g. `export AI_URL=https://***.cognitiveservices.azure.com/`
key = os.getenv('AI_SECRET', 'SETENVVAR!') 
endpoint = os.getenv('AI_URL', 'SETENVVAR!') 

# Authenticate the client using your key and endpoint 
def authenticate_client():
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=ta_credential)
    return text_analytics_client

client = authenticate_client()

# Example method for summarizing text
def ai_summarize_txt(client, document):
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import (
        TextAnalyticsClient,
        ExtractSummaryAction
    ) 

    poller = client.begin_analyze_actions(
        document,
        actions=[
            ExtractSummaryAction(max_sentence_count=4)
        ],
    )

    summarized_text = ""
    document_results = poller.result()
    for result in document_results:
        extract_summary_result = result[0]  # first document, first result
        if extract_summary_result.is_error:
            logging.info("...Is an error with code '{}' and message '{}'".format(
                extract_summary_result.code, extract_summary_result.message
            ))
        else:
            summarized_text += "Summary extracted: \n{}".format(
                " ".join([sentence.text for sentence in extract_summary_result.sentences]))
            logging.info(f"Returning summarized text:  \n{summarized_text}")
    return summarized_text


@app.function_name(name="summarize_function")
@app.blob_trigger(arg_name="myblob", path="test-samples-trigger/{name}",
                  connection="blobstorage")
@app.blob_output(arg_name="outputblob", path="test-samples-output/{name}-output.txt", connection="blobstorage")
def test_function(myblob: func.InputStream, outputblob: func.Out[str]):
   logging.info(f"Triggered item: {myblob.name}\n")

   document = [myblob.read().decode('utf-8')]
   summarized_text = ai_summarize_txt(client, document)
   logging.info(f"\n *****Summary  PAULTEST***** \n{summarized_text}");
   outputblob.set(summarized_text)

   #return summarized_text
