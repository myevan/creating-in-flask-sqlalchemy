from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.sqlalchemy import SignallingSession
from flask.ext.sqlalchemy import get_state
from flask.ext.sqlalchemy._compat import itervalues

from sqlalchemy.orm.scoping import scoped_session, instrument
from contextlib import contextmanager


class ShardedSQLAlchemy(SQLAlchemy):
    class ShardedSession(SignallingSession):
        def __init__(self, *args, **kwargs):
            SignallingSession.__init__(self, *args, **kwargs)
            self._shard_index = None

        @contextmanager
        def sharding(self, id):
            app_config = self.app.config
            self._shard_index = (id & app_config.get('SQLALCHEMY_SHARD_MASK', 0xff)) >> app_config.get('SQLALCHEMY_SHARD_SHIFT', 8)
            print self._shard_index
            yield
            self._shard_index = None

        def get_bind(self, mapper, clause=None):
            # mapper is None if someone tries to just get a connection
            if mapper is not None:
                info = getattr(mapper.mapped_table, 'info', {})
                bind_key = info.get('bind_key')
                if bind_key is not None:
                    state = get_state(self.app)

                    if type(bind_key) is list:
                        return state.db.get_engine(self.app, bind=bind_key[self._shard_index])
                    else:
                        return state.db.get_engine(self.app, bind=bind_key)

            return super(SignallingSession, self).get_bind(mapper, clause)

    def __init__(self, *args, **kwargs):
        setattr(scoped_session, 'sharding', instrument('sharding'))
        SQLAlchemy.__init__(self, *args, **kwargs)

    def create_session(self, options):
        return self.ShardedSession(self, **options)

    def get_tables_for_bind(self, bind=None):

        result = []
        for table in itervalues(self.Model.metadata.tables):
            table_bind_key = table.info.get('bind_key')
            if type(table_bind_key) is list and bind in table_bind_key:
                result.append(table)
            else:
                if table.info.get('bind_key') == bind:
                    result.append(table)
        return result

