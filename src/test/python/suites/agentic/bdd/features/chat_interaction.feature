Feature: Chat Interaction
  As a developer
  I want to interact with the agent via chat
  So that I can get information about environments and provision resources

  Scenario: Send a greeting
    Given the agent API is accessible
    When I send a chat message "hello"
    Then the chat response is not empty
    And the chat response has a thread ID

  Scenario: Query environment status
    Given the agent API is accessible
    When I send a chat message "what environments are running?"
    Then the chat response is not empty
