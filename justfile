# List all recipies
default:
    just --list --unsorted

# Run all fmt and clippy checks
check:
    just --check --fmt --unstable
    cargo +nightly fmt --check
    cargo clippy -- -D warnings

# Build the runtime
build:
    RUST_LOG=frameless=info cargo build --release

# Run the node with the runtime
run: build
    RUST_LOG=frameless=debug pba-omni-node --runtime ./target/release/wbuild/runtime/runtime.wasm --tmp --consensus manual-seal-1000

# Run the tests
test:
    cargo test -- --nocapture
