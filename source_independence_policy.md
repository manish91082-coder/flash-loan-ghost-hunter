# Source Independence Policy
- **True Independence:** Different derivation graphs (e.g., Chain RPC vs Off-chain orderbook).
- **Independent Observation:** Two distinct RPC nodes reading the same upstream chain state.
- **False Independence (Same Upstream):** Two APIs calling the identical endpoint.
