import torch


def steering_hook_factory(
    truthfulness_vector,
    alpha,
):
    """
    Create an activation-steering hook.

    Research methodology:
        activation + alpha * truthfulness_vector

    The vector is prepared once before the hook is created,
    rather than being moved/converted on every hook call.
    """

    def steering_hook(
        activation,
        hook,
    ):
        return activation + (
            alpha * truthfulness_vector
        )

    return steering_hook


def generate_baseline(
    model,
    prompt,
    max_new_tokens=60,
):
    """
    Generate the unsteered baseline response.
    """

    with torch.no_grad():

        return model.generate(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )


def generate_steered(
    model,
    prompt,
    layer,
    truthfulness_vector,
    alpha,
    max_new_tokens=60,
):
    """
    Generate a response with activation steering.

    Steering location:
        blocks.{layer}.hook_resid_post

    Steering equation:
        activation + alpha * truthfulness_vector
    """

    hook_name = (
        f"blocks.{layer}.hook_resid_post"
    )

    # --------------------------------------------------------
    # Prepare vector ONCE before generation.
    # --------------------------------------------------------

    vector = truthfulness_vector.to(
        device=model.cfg.device,
        dtype=model.cfg.dtype,
    )

    hook = steering_hook_factory(
        vector,
        alpha,
    )

    with torch.no_grad():

        with model.hooks(
            fwd_hooks=[
                (hook_name, hook)
            ]
        ):

            output = model.generate(
                prompt,
                max_new_tokens=max_new_tokens,
                do_sample=False,
            )

    return output
