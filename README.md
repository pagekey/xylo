# xylo

Self-hosted app creation kit.

## Getting Started

1. Generate a project:

```bash
xylo new myproject
```

2. Enter the project:

```bash
cd myproject
```

3. Start the development servers:

```bash
xylo dev
```

4. Visit the frontend at http://localhost:3000.

5. Send a request to the backend:

```bash
curl http://localhost:5000
```

## Installation

For now, there is no way to install the CLI other than to clone this repository and use `cargo build` to get a `xylo` executable in the `target/debug` directory, or replace all instances of `xylo` with `cargo run`.
