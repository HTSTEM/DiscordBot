# `discord-bot`

This is the Discord bot for HTSTEM server.

## Configuring

Create a file named `config.yml`. Put this inside of it:

```yml
token: <token here>
```

Debugging the bot? Put this inside, too:

```yml
debug_mode: true
debug:
  token: <token to your debugging bot>
token: <token to the real bot>
```

As you can see, inside of `debug` is a complete copy of the outer config. It's like a **subconfig**. It's only applied
when `debug` is true.

When `debug` is true, the bot will work **everywhere**, and the command prefix is changed to `..` instead of the usual
`sb?`.
