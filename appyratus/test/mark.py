from pytest import mark

# High-level
unit = mark.unit
integration = mark.integration
performance = mark.performance
slow = mark.slow
skip = mark.skip
# XXX It may seem ubiquitous to shorten parametrize to params,
# however in the right context you should import this module
# entirely, referenced as `mark.params`, and not be concerned
# otherwise.  It is worth mentioning that in it's next incarnation,
# it will be a better `params` method entirely
params = mark.parametrize
