import theano
import theano.tensor as T
import numpy as np
from theano.printing import Print

def recurrence_pass(start_idx, log_probs):
    log_init_probs = T.alloc(-np.inf, log_probs.shape[1], log_probs.shape[2])
    log_init_probs = T.set_subtensor(
            log_init_probs[T.arange(log_init_probs.shape[0]), start_idx], 0)
    pass_log_probs, _ = theano.scan(
        fn=recurrence,
        sequences=[log_probs],
        outputs_info=[log_init_probs]
    )
    return pass_log_probs

def recurrence(log_p_curr, log_p_prev):
    # normalise and bring back to p space
    k = T.max(log_p_prev, axis=1, keepdims=True)
    norm_p_prev = T.switch(
            T.isinf(log_p_prev), 0, T.exp(log_p_prev - k))  # set -inf to 0

    # previous
    _result = norm_p_prev
#    _result = Print("_result")(_result)
    # add shift of previous
    _result = T.inc_subtensor(_result[:, 1:],   norm_p_prev[:, :-1])
    # add skips of previous
    _result = T.inc_subtensor(_result[:, 3::2], norm_p_prev[:, 1:-2:2])
    # current
    # log(p) should be 0 for first 2 terms
    result = T.switch(T.eq(_result, 0), -np.inf,
                        log_p_curr + T.log(_result) + k)
    return result
