param name string
param location string = resourceGroup().location
param tags object = {}

module aiLanguageService '../core/cognitive/ai-textanalytics.bicep' = {
  name: 'ai-textanalytics'
  params: {
    aiResourceName: name
    location: location
    tags: tags
  }
}

output name string = aiLanguageService.name
output url string = aiLanguageService.outputs.url
