import gc

import torch


def extract_activation(
    model,
    prompt,
    layer,
):
    """
    Extract the final-token residual-stream activation
    from the requested Transformer layer.
    """

    tokens = model.to_tokens(prompt)

    hook_name = f"blocks.{layer}.hook_resid_post"

    def layer_filter(name):
        return name == hook_name

    with torch.no_grad():

        _, cache = model.run_with_cache(
            tokens,
            names_filter=layer_filter,
            return_type=None,
        )

        activation = (
            cache[hook_name][0, -1, :]
            .detach()
            .clone()
            .cpu()
        )

    del cache
    del tokens

    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return activation


def extract_direction(
    model,
    question,
    truthful,
    false,
    layer,
    build_prompt,
):
    """
    Calculate:

        truthful activation - false activation
    """

    truthful_prompt = build_prompt(
        question,
        truthful,
    )

    false_prompt = build_prompt(
        question,
        false,
    )

    truthful_activation = extract_activation(
        model=model,
        prompt=truthful_prompt,
        layer=layer,
    )

    false_activation = extract_activation(
        model=model,
        prompt=false_prompt,
        layer=layer,
    )

    direction = (
        truthful_activation
        - false_activation
    )

    return direction
