param name string
param location string = resourceGroup().location
param tags object = {}
param customSubDomainName string

module aiLanguageService '../core/cognitive/ai-textanalytics.bicep' = {
  name: 'ai-textanalytics'
  params: {
    aiResourceName: name
    location: location
    tags: tags
    customSubDomainName: customSubDomainName
  }
}

output name string = aiLanguageService.outputs.name
output url string = aiLanguageService.outputs.url
