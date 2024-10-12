param aiResourceName string
param location string = resourceGroup().location
param tags object = {}
param sku string = 'S'
param customSubDomainName string

param principalIds array = []

resource cognitiveService 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: aiResourceName
  sku: {
    name: sku
  }
  tags: tags
  location: location
  kind: 'TextAnalytics'
  properties: {
    customSubDomainName: customSubDomainName
  }
}

output name string = cognitiveService.name
output url string = cognitiveService.properties.endpoint
