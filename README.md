# `discord-bot`

This is the Discord bot for HTSTEM server.

## Configuring

Create a file named `config.yml`. Put this inside of it:

```yml
token: <token here>
```

Debugging the bot? Put this inside, too:

```yml
debug_token: <token to your debugging bot>
debug: true
token: <token to the real bot>
```

When you have `debug: true`, the `debug_token` is used instead of `token`. If `debug` is true and there is no
`debug_token`, `token` is used instead.

When `debug` is true, the bot will work **everywhere**, and the command prefix is changed to `..` instead of the usual
`sb?`.
