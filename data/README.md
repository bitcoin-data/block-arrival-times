# Data Sources

- contributed by [Vojtěch Strnad](https://github.com/vostrnad)
    - `vostrnad_node1.csv` from a Bitcoin Core debug.log

- contributed by [OliverOffing](https://github.com/OliverOffing)
    - `offing-gcp.csv` from a Bitcoin Core debug.log

- contributed by [KIT DSN Bitcoin Monitoring](https://www.dsn.kastel.kit.edu/bitcoin/)
    - `KIT_monitor1.csv`
    - `KIT_monitor2.csv`
    - `KIT_monitorB.csv`

- contributed by [n-thumann](https://github.com/n-thumann)
    - `n-thumann.csv` from a Bitcoin Core debug.log

- contributed by [darosior](https://github.com/darosior)
    - `darosior_node0.csv` from a Bitcoin Core debug.log

- contributed by [bboerst](https://github.com/bboerst)
    - `stratum_work_empty.csv` export from [stratum.work](https://github.com/bboerst/stratum-work) dataset with timestamps for the first `mining.notify` (block template) sent for each height. `empty` in the filename means first jobs that have empty merkles. Note: since a `mining.notify` at height N means the pool just observed block N-1, the timestamp represents the arrival time of block N-1.
    - `stratum_work_not_empty.csv` same export but showing first jobs with `non-empty` merkles

- contributed by [0xB10C](https://github.com/0xb10c)
    - `0xb10c_memo-old.csv` old mempool.observer database (ZMQ based timestamps)
    - `0xb10c_memo.csv` newer mempool.observer database (ZMQ based timestamaps)
    - `0xb10c_monitoring1.csv` export from general monitoring (ZMQ based timestamps)
    - `0xb10c_rs2.csv` exported from a debug.log
    - `0xb10c_peer-observer-*.csv` exported from peer-observer Bitcoin Core node debug.logs
