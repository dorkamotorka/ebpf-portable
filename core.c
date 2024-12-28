//go:build ignore
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>

char _license[] SEC("license") = "GPL";

SEC("tracepoint/tcp/tcp_retransmit_skb")
int tcp_retransmit_skb(struct trace_event_raw_tcp_event_sk_skb *ctx) {
        __u16 sport;
        __u16 dport;
        __u16 family;

	BPF_CORE_READ_INTO(&sport, ctx, sport);
	BPF_CORE_READ_INTO(&dport, ctx, dport);
	BPF_CORE_READ_INTO(&family, ctx, family);

	// Print fields
    	bpf_printk("sport: %u, dport: %u, family: %u\n", sport, dport, family);
	return 0;
}
