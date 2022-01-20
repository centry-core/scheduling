from flask import render_template


def render_security_test_create(context, slot, payload):
    return render_template(
        'security_scheduling:security_test_create.html',
        config=payload
    )
