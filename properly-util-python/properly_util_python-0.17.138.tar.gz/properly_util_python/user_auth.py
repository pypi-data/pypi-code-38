import logging
from properly_util_python.table_helper import TableHelper
from botocore.exceptions import ClientError
import traceback
from boto3.dynamodb.conditions import Key
import time
from properly_util_python.dynamo_data_utils import DynamoData

from properly_util_python.schemas import UserSchema
from properly_util_python.dynamo_helper import DynamoHelperBase


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class UserAuthHelper:

    OPERATIONS_ROLE_ID = "S4jlPBglYkqccBcWody6hw"
    BASIC_ROLE_ID = "jczqf4GgkEKd1bxtTgpJOg"

    def __init__(self, dynamo_helper: DynamoHelperBase):
        self.dynamo_helper = dynamo_helper
        self.table_helper = TableHelper(self.dynamo_helper)
        self.user_table = self.table_helper.get_table(TableHelper.USER_TABLE_NAME)


    #for overview see: https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html
    # for specific claims see: http://openid.net/specs/openid-connect-core-1_0.html#StandardClaims
    # one of the best summaries of relevant fields: https://medium.com/@darutk/understanding-id-token-5f83f50fa02e
    def get_user_auth_context_from_event(self, event):

        logger.info("event type is: {} ".format(type(event)))

        if event is None:
            logger.info("event is none")
            return None


        requestContext = event.get("requestContext")
        if requestContext is None:
            logger.warning("request context is none")
            return None

        authorizer = requestContext.get("authorizer")
        if authorizer is None:
            logger.warning("authorizer is none")
            return None

        claims = authorizer.get("claims")
        if claims is None:
            logger.warning("claims is none")
            return None

        email = claims.get("email")
        if ((not isinstance(email, str)) or (email == "")):
            logger.warning("email none, invalid type, or empty")
            return None

        sub = claims.get("sub")
        if ((not isinstance(sub, str)) or (sub == "")):
            logger.warning("sub none, invalid type, or empty")
            return None

        is_email_verified = claims.get("email_verified")
        if is_email_verified is None:
            logger.info("email is verified is none")
            #remove early exit, see note below
            #return None

        #default false
        is_email_verified_bool = False
        if ( isinstance(is_email_verified, bool) and (is_email_verified) ):
            #specifically boolean type and true
            logger.info("email verified found as boolean true")
            is_email_verified_bool = True
        elif (is_email_verified == "true"):
            #specifically a string containing true
            logger.info("email verified found as string 'true'")
            is_email_verified_bool = True

        if not is_email_verified_bool:
            #Previously: don't accept unconfirmed email
            #return None
            #Now: this check is weakened by allowing jwt without email verified explicitly set
            #reasoning, the connected systems only provide verified emails, but, that could change
            # facebook : https://stackoverflow.com/a/11847514/7632432
            # google : https://stackoverflow.com/a/30357942/7632432
            # amazon : can't confirm without email as currently configured:
            #           https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-email-phone-verification.html
            logger.info("strict mode would not pass login due to verified flag")
            pass


        user_auth_context = {'auth_id': sub,
                             'auth_email': email}

        return user_auth_context


    #From: https://docs.google.com/document/d/1j6hsvKSra6HkwxFRBKnfEy_wr8nCxYn0oSO8Of5SqUE/edit
    #
    #  returns a valid properly_user_id or None if there was an unauthorizied condition

    def find_or_update_verified_user(self, user_auth: dict, requested_properly_user_id: str):

        auth_id = user_auth.get('auth_id')
        auth_email = user_auth.get('auth_email')
        actual_properly_user_id = self.get_properly_id_from_user_auth_id(auth_id)

        if (actual_properly_user_id):
            logger.info("Existing Verified:  properly user id: {}  auth id: {}".format(actual_properly_user_id,
                                                                                       auth_id))
            return actual_properly_user_id


        #was not found, so some update will be attempted
        id_to_update = requested_properly_user_id

        actual_properly_user_id = self.get_properly_id_from_user_auth_email(auth_email)
        if (actual_properly_user_id):
            logger.info("Existing found:  properly user id: {}  with email: {}".format(actual_properly_user_id,
                                                                                       auth_email))
            #use the matching id
            id_to_update = actual_properly_user_id


        actual_properly_user_id = self.create_or_update_if_unverified(id_to_update, auth_id, auth_email)
        if not actual_properly_user_id:
            logger.error("Failed to update properly user id: {}  with user auth: {}. ".format(actual_properly_user_id,
                                                                                       user_auth))
            #will occur when something is invalid about the target record to update (some other user claimed, or different email etc.)
            return None
        return actual_properly_user_id



    def get_properly_id_from_user_auth_id(self, auth_id: str):

        key_condition = Key('authIdCognito').eq(auth_id)


        response = self.user_table.query(
            IndexName='authIdCognito-index',
            KeyConditionExpression=key_condition,

        )
        items = response.get('Items')
        if (len(items)>1):
            logger.error("more than one user assoicated with auth id: {}".format(auth_id))
        item = None
        for item_candidate in items[:1]:
            item = item_candidate  # use the first one found

        if item is None:
            return None

        properly_user_id = item.get('id')

        return properly_user_id


    def get_properly_id_from_user_auth_email(self, auth_email: str):

        key_condition = Key('unverifiedEmail').eq(auth_email)

        response = self.user_table.query(
            IndexName='unverifiedEmail-index',
            KeyConditionExpression=key_condition,

        )
        items = response.get('Items')
        if (len(items) > 1):
            logger.error("more than one user associated with auth email: {}".format(auth_email))

        item = None
        for item_candidate in items[:1]:
            item = item_candidate  # use the first one found

        if item is None:
            return None

        properly_user_id = item.get('id')

        return properly_user_id


    def create_or_update_by_properly_id(self, requested_properly_user_id, user_auth):

        return "INVALID_ID_NOT_IMPLEMENTED"

    def create_or_update_if_unverified(self, properly_user_id, auth_id: str, auth_email: str):

        seconds_epoch_now = int(time.time())

        user_key = {'id': properly_user_id}


        expression_attributes = {':updatedAt':seconds_epoch_now,
                                 ':email': auth_email,
                                 ':authIdCognito': auth_id}



        update_expression = 'set updatedAt = :updatedAt, ' \
                            'verifiedEmail = :email,'  \
                            'authIdCognito = :authIdCognito, '\
                            'unverifiedEmail = :email, '\
                            'createdAt = if_not_exists(createdAt,:updatedAt)'


        #condition represents the idea that:
        # This account is unverified or verifed to the same id (can't verify already verified accounts)
        # and if the unverfiedEmail either doesn't exist or is the same value (can't verify unverfied accounts with different email)
      #  condition_expression = '( attribute_not_exists(authCognitoId) OR (authCognitoId = :authCognitoId) ) ' \
      #                         ' AND (attribute_not_exists(unverifiedEmail) OR (unverifiedEmail = :email) )'

        condition_expression = '(  authIdCognito = :authIdCognito OR attribute_not_exists(authIdCognito)  ) ' \
                                 ' AND (unverifiedEmail = :email OR attribute_not_exists(unverifiedEmail) ) '

        try:

            response = self.user_table.update_item(
                Key=user_key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attributes,
                ConditionExpression = condition_expression,
                ReturnValues='ALL_NEW'
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return None
            logger.error("exception traceback: {}".format(traceback.format_exc()))

            raise

        return properly_user_id


    def is_user_in_role_for_offer(self, properly_user_id, role_id, offer_id):
        #todo: this is a way of implementing "operations manager for calgary can see calgary deals"
        # or "assigned appraiser can see offers they are assigned to"
        # this is not implemented yet, just using global role check until this capability is required
        raise NotImplementedError("roles for a resource is not implemented")

    #accepts None or empty user_id and role_id
    def is_user_in_role(self, properly_user_id: str, role_id: str):

        if (not isinstance(properly_user_id, str) or (properly_user_id == "" ) ):
            return False #None or empty users are in no role


        user_table = self.table_helper.get_table(TableHelper.USER_TABLE_NAME)

        response = user_table.get_item(Key={UserSchema.ID: properly_user_id},) #Consider: ConsistentRead=True

        user_dict_dynamo = response.get('Item')
        if (user_dict_dynamo is None):
            return False  # not in a role if the user doesn't exist

        if (role_id == UserAuthHelper.BASIC_ROLE_ID):
            return True  # if the user exists they are automatically in the basic role

        user_dict = DynamoData.to_dict(user_dict_dynamo)

        roles_array = user_dict.get(UserSchema.ROLES)

        if (roles_array is None):
            return False

        has_role_flag = role_id in roles_array

        return has_role_flag



