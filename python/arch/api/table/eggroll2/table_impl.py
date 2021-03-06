#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import uuid
from typing import Iterable

from arch.api.utils.profile_util import log_elapsed

from arch.api.table.table import Table


# noinspection SpellCheckingInspection,PyProtectedMember,PyPep8Naming
class DTable(Table):

    def __init__(self, dtable, session_id):
        self._dtable = dtable
        self._partitions = self._dtable.get_partitions()
        self.schema = {}
        self._name = self._dtable.get_name() or str(uuid.uuid1())
        self._namespace = self._dtable.get_namespace()
        self._session_id = session_id

    @classmethod
    def from_dtable(cls, session_id, dtable):
        return DTable(dtable=dtable, session_id=session_id)

    def get_name(self):
        return self._name

    def get_namespace(self):
        return self._namespace

    def dtable(self):
        return self._dtable

    @log_elapsed
    def save_as(self, name, namespace, partition=None, use_serialize=True, **kwargs):
        from arch.api import RuntimeInstance
        persistent_engine = RuntimeInstance.SESSION.get_persistent_engine()
        # saved_table = self._dtable.save_as(name=name,
        #                                    namespace=namespace,
        #                                    partition=partition,
        #                                    use_serialize=use_serialize,
        #                                    persistent_engine=persistent_engine)
        options = dict()
        options['store_type'] = persistent_engine
        saved_table = self._dtable.save_as(name=name, namespace=namespace, partition=partition, options=options)
        return self.from_dtable(self._session_id, saved_table)

    def put(self, k, v, use_serialize=True, maybe_large_value=False):
        if not maybe_large_value:
            return self._dtable.put(k=k, v=v)
        else:
            from arch.api.table.storage_enhance import split_put
            return split_put(k, v, use_serialize=True, put_call_back_func=self._dtable.put)

    def put_all(self, kv_list: Iterable, use_serialize=True, chunk_size=100000):
        #return self._dtable.put_all(kv_list=kv_list, use_serialize=use_serialize, chunk_size=chunk_size)
        options = {}
        return self._dtable.put_all(kv_list, options=options)

    def get(self, k, use_serialize=True, maybe_large_value=False):
        if not maybe_large_value:
            return self._dtable.get(k, use_serialize)
        else:
            from arch.api.table.storage_enhance import split_get
            return split_get(k=k, use_serialize=use_serialize, get_call_back_func=self._dtable.get)

    @log_elapsed
    def collect(self, min_chunk_size=0, use_serialize=True, should_sort=True, **kwargs) -> list:
        return self.get_all(should_sort=should_sort)

    @log_elapsed
    def get_all(self, should_sort=True):
        ret = self._dtable.get_all()
        if should_sort:
            ret = sorted(ret, key=lambda x: x[0])
        return ret

    def delete(self, k, use_serialize=True):
        return self._dtable.delete(k=k)

    def destroy(self):
        return self._dtable.destroy()

    @log_elapsed
    def count(self, **kwargs):
        return self._dtable.count()

    def put_if_absent(self, k, v, use_serialize=True):
        return self._dtable.put_if_absent(k=k, v=v, use_serialize=use_serialize)

    def take(self, n=1, keysOnly=False, use_serialize=True):
        options = {}
        options['keys_only'] = keysOnly
        return self._dtable.take(n=n, options=options)

    def first(self, keysOnly=False, use_serialize=True):
        options = {}
        options['keys_only'] = keysOnly
        return self._dtable.first(options=options)

    # noinspection PyProtectedMember
    def get_partitions(self):
        return self._dtable.get_partitions()

    """
    computing apis
    """

    @log_elapsed
    def map(self, func, **kwargs):
        return DTable(self._dtable.map(func), session_id=self._session_id)

    @log_elapsed
    def mapValues(self, func, **kwargs):
        print("DTable mapValues")
        return DTable(self._dtable.map_values(func), session_id=self._session_id)

    @log_elapsed
    def mapPartitions(self, func, **kwargs):
        #return DTable(self._dtable.map_partitions(func), session_id=self._session_id)
        return DTable(self._dtable.collapse_partitions(func), session_id=self._session_id)

    @log_elapsed
    def collapsePartitions(self, func, **kwargs):
        return DTable(self._dtable.collapse_partitions(func), session_id=self._session_id)

    @log_elapsed
    def reduce(self, func, **kwargs):
        return self._dtable.reduce(func)

    @log_elapsed
    def join(self, other, func, **kwargs):
        return DTable(self._dtable.join(other._dtable, func=func), session_id=self._session_id)

    @log_elapsed
    def glom(self, **kwargs):
        return DTable(self._dtable.glom(), session_id=self._session_id)

    @log_elapsed
    def sample(self, fraction, seed=None, **kwargs):
        return DTable(self._dtable.sample(fraction=fraction, seed=seed), session_id=self._session_id)

    @log_elapsed
    def subtractByKey(self, other, **kwargs):
        return DTable(self._dtable.subtract_by_key(other._dtable), session_id=self._session_id)

    @log_elapsed
    def filter(self, func, **kwargs):
        return DTable(self._dtable.filter(func), session_id=self._session_id)

    @log_elapsed
    def union(self, other, func=lambda v1, v2: v1, **kwargs):
        return DTable(self._dtable.union(other._dtable, func=func), session_id=self._session_id)

    @log_elapsed
    def flatMap(self, func, **kwargs):
        _temp_table = self.from_dtable(self._session_id, self._dtable.flat_map(func))
        return _temp_table.save_as(name=f"{_temp_table._name}.save_as", namespace=_temp_table._namespace)
