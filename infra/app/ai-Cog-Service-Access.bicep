param principalID string
param principalType string = 'ServicePrincipal' // Workaround for https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-template#new-service-principal
param roleDefinitionID string
param aiResourceName string

resource cognitiveService 'Microsoft.CognitiveServices/accounts@2021-10-01' existing = {
  name: aiResourceName
}

// Allow access from API to storage account using a managed identity and least priv Storage roles
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(cognitiveService.id, principalID, roleDefinitionID)
  scope: cognitiveService
  properties: {
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionID)
    principalId: principalID
    principalType: principalType 
  }
}

output ROLE_ASSIGNMENT_NAME string = storageRoleAssignment.name
