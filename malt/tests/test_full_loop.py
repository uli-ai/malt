# import pytest
import faulthandler
faulthandler.enable()

import logging
logging.basicConfig(level="DEBUG")


def test_full_loop():
    import torch
    import malt

    net = malt.models.supervised_model.SimpleSupervisedModel(
        # graph -> latent
        representation=malt.models.representation.DGLRepresentation(
            out_features=128
        ),

        # latent -> parameters
        regressor=malt.models.regressor.NeuralNetworkRegressor(
            in_features=128, out_features=1
        ),

        # parameters -> likelihood
        likelihood=malt.models.likelihood.HomoschedasticGaussianLikelihood(),
    )

    policy = malt.policy.Greedy(
        utility_function=malt.policy.utility_functions.expected_improvement,
    )

    trainer = malt.trainer.get_default_trainer()
    center = malt.agents.center.NaiveCenter(name="NaiveCenter")
    vendor, assayer = malt.fake_tasks.collections.count_carbons()

    player = malt.agents.player.AutonomousPlayer(
        name="AutonomousPlayer",
        center=center,
        policy=policy,
        model=net,
        trainer=trainer,
    )

    center.register(vendor)
    center.register(assayer)
    center.register(player)

    catalogue = vendor.catalogue()()

    while len(player.portfolio) < len(catalogue):
        points_to_acquire = player.prioritize(catalogue-player.portfolio)
        query_receipt = player.query(
            points_to_acquire,
            vendor=vendor,
            assayers=[assayer],
        )
        assert query_receipt is not None
        quote = player.check(query_receipt)
        order_receipt = player.order(quote)
        assert order_receipt is not None
        report = player.check(order_receipt)[0]
        player.portfolio += report.points
        player.train()

    print([len(point.smiles) for point in player.portfolio])

test_full_loop()
