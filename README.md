# signalfx-bridge

Bridge Aiven service metrics to SignalFX

Currently only the following host and kafka metrics are supported

## Host metrics

- cpu.utilization
- df_complex.used
- df_complex.free
- disk_ops.read
- disk_ops.write
- disk.utilization
- if_errors.rx
- if_errors.tx
- if_octets.rx
- if_octets.tx
- load.longterm
- load.midterm
- load.shortterm
- memory.active
- memory.buffered
- memory.cached
- memory.free
- memory.inactive
- memory.used
- memory.utilization
- memory.wired
- network.total
- vmpage_io.swap.in
- vmpage_io.swap.out

## Kafka metrics

- counter.kafka-bytes-in
- counter.kafka-bytes-out
- counter.kafka.fetch-consumer.total_time.count
- counter.kafka.fetch-follower.total_time.count
- counter.kafka-isr-expands
- counter.kafka-isr-shrinks
- counter.kafka-leader-election-rate
- counter.kafka.logs.flush-time.count
- counter.kafka-messages-in
- counter.kafka.produce.total_time.count
- counter.kafka-unclean-election-rate
- gauge.kafka-active-controllers
- gauge.kafka-offline-partitions-count
- gauge.kafka-underreplicated-partitions
