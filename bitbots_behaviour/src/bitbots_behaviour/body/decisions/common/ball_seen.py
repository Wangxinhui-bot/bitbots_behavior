"""
BallSeen
^^^^^^^^^^^^^

.. moduleauthor:: Martin Poppinga <1popping@informatik.uni-hamburg.de>

"""
import time

import rospy
from body.actions.search import Search
from body.decisions.common.close_ball import CloseBallPenaltyKick, CloseBallCommon
from body.decisions.goalie.ball_dangerous import BallDangerous
from body.decisions.team_player.fieldie_search_decision import FieldieSearchDecision
from stackmachine.abstract_decision_module import AbstractDecisionModule


class AbstractBallSeen(AbstractDecisionModule):
    """
    Entscheidet ob der Ball gesehen wurde bzw. ob die Informationen zuverlässig genug sind
    Decides if the ball was seen rspectively if the information is  authentic enough.
    """

    def __init__(self, _):
        super(AbstractBallSeen, self).__init__()
        self.max_ball_time = rospy.get_param("/Behaviour/Common/maxBallTime")

    def perform(self, connector, reevaluate=False):

        if (time.time() - connector.vision.ball_last_seen()) < self.max_ball_time:
            return self.has_ball_seen(connector)
        else:
            return self.ball_not_seen(connector)

    def get_reevaluate(self):
        return True

    def has_ball_seen(self, connector):
        raise NotImplementedError

    def ball_not_seen(self, connector):
        raise NotImplementedError


class BallSeenGoalie(AbstractBallSeen):
    def perform(self, connector, reevaluate=False):

        if time.time() - connector.blackboard_capsule().get_confirmed_ball() < 2:
            return self.has_ball_seen(connector)
        else:
            return self.ball_not_seen(connector)

    def has_ball_seen(self, connector):
        return self.push(BallDangerous)

    def ball_not_seen(self, connector):
        return self.push(Search)


class BallSeenFieldie(AbstractBallSeen):
    """
    def perform(self, connector, reevaluate=False):

        if connector.raw_vision_capsule().ball_seen() or \
                ((time.time() - connector.blackboard_capsule().get_confirmed_ball() < 5 and
                connector.filtered_vision_capsule().get_local_goal_model_ball_distance() > 1000)
            or (time.time() - connector.blackboard_capsule().get_confirmed_ball() < 2 and
                connector.filtered_vision_capsule().get_local_goal_model_ball_distance() < 1000)):
            return self.has_ball_seen(connector)
        else:
            return self.ball_not_seen(connector)
    """

    def has_ball_seen(self, connector):
        return self.push(CloseBallCommon)

    def ball_not_seen(self, connector):
        return self.push(FieldieSearchDecision)


class BallSeenPenaltyKick(AbstractBallSeen):
    def has_ball_seen(self, connector):
        return self.push(CloseBallPenaltyKick)

    def ball_not_seen(self, connector):
        return self.push(Search)
