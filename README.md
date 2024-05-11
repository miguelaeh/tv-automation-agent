# Pipeless Agent for TV automation

This agent turns off the TV when nobody is watching it.

This agent works along with the Pipeless Agent Home Assistant Integration.

See the complete tutorial at: LINK VIDEO HERE


## Logic of the agent

```mermaid
graph TD;
    A[start] --> B{Person};
    B --> |No| C{TV};
    B --> |Yes| A;
    C --> |ON| D{IdleTime};
    C --> |OFF| A;
    D --> |Passed| E[Call Webhook];
    D --> |Not passed| A;
    E --> A;
```
