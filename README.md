# shellmcp
Expose Shell Commands as MCP tools

## Step 1: write shell command definitions

```yml
server:
  name: filesystem-mcp
  desc: MCP Server for filesystem operations
tools:
  ListFiles:
    cmd: ls -la $@
    help-cmd: ls --help
    desc: |
      List files in the current directory
  GrepExtract:
    cmd: grep -O $PATTERN $FILE
    args:
     - name: PATTERN
       help: pattern for grep
     - name: FILE
       help: file parh for grep
```

## Step 2: generate an MCP server executable 

```sh
shellmcp generate server.yml --out ~/.local/bin/filesystem-mco
```

## Step 3: configure mcp.json

```json
TODO
```

## Step 4: DONE! Use tools 
