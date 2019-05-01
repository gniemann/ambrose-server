from typing import Type, Optional, AnyStr

from cryptography.fernet import Fernet

from ambrose.common import db_transaction
from ambrose.models import Account, User
from ambrose.services import UnauthorizedAccessException


class AccountService:
    _model_registry = {}
    _registry = {}

    def __init_subclass__(cls, model: Type[Account], **kwargs):
        super(AccountService, cls).__init_subclass__(**kwargs)
        cls._model_registry[model.__name__] = cls
        idx = cls.__name__.index('AccountService')
        cls._registry[cls.__name__[:idx].lower()] = cls

    def __new__(cls, account: Optional[Account], cipher: Optional[Fernet] = None):
        if not account:
            return super().__new__(cls)

        service_type = cls._model_registry[account.__class__.__name__]
        return super().__new__(service_type)

    def __init__(self, account: Optional[Account], cipher: Optional[Fernet] = None):
        self.cipher = cipher
        self.account = account

    def _encrypt(self, token: str) -> str:
        return self.cipher.encrypt(token.encode('utf-8')).decode('utf-8')

    def _decrypt(self, token: AnyStr) -> str:
        if not isinstance(token, bytes):
            token = token.encode('utf-8')
        return self.cipher.decrypt(token).decode('utf-8')

    @classmethod
    def get_account(self, account_id: int, user: User) -> Account:
        account = Account.by_id(account_id)
        if account not in user.accounts:
            raise UnauthorizedAccessException()

        return account

    def get_task_statuses(self):
        pass

    @classmethod
    def create_account(cls, account_type: str, cipher: Fernet, user: User, *args, **kwargs) -> Account:
        service_type = cls._registry[account_type.lower()]
        service = service_type(None, cipher)
        return service.new_account(user, *args, **kwargs)

    def _new_account(self, *args, **kwargs) -> Account:
        pass

    def new_account(self, user: User, *args, **kwargs) -> Account:
        with db_transaction():
            account = self._new_account(*args, **kwargs)
            user.add_account(account)
            self.account = account
            return account

    def edit_account(self, *args, **kwargs):
        pass