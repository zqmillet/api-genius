定义模型
========

API-Genius 的中的模型是基于 sqlalchemy 的, 并且对 sqlalchemy 的模型进行一系列扩展.

.. code-block:: python

    from api_genius import Column
    from api_genius import Base
    from sqlalchemy import String
    from sqlalchemy import Integer
    from sqlalchemy import Float
    from sqlalchemy import Date
    from sqlalchemy import DateTime
    from sqlalchemy import func

    class User(Base):
        __tablename__ = 'users'

        id = Column(String(50), autoincrement=True, primary_key=True, readonly=True)
        name = Column(String(50), nullable=False)
        birthday = Column(Date(), comment='生日', readonly=True)
        department_id = Column(String(50), nullable=False, comment='部门 ID')
        entry_date = Column(Date(), default=func.now(), readonly=True, comment='入职时间')
        weight = Column(Float(), less_than_or_equal_to=100, comment='体重, 单位 kg')
        height = Column(Float(), greater_than=150, comment='身高, 单位 cm')
        update_time = Column(DateTime(), readonly=True, comment='更新时间')
        _signature = Column(String(60), alias='signature', default=get_signature)

API-Genius 提供的 :py:obj:`Column` 继承自 sqlalchemy 的 :py:obj:`Column`, 并在此基础上进行一系列扩展.

对于一个数据来说, 需要 Access Modifier, 即访问修饰符, API-Genius 沿用了 Python 风格的 Access Modifier:

- 如果成员变量前缀是 ``_``, 表示 Private, 对 API 不可见.
- 如果成员变量前缀不是 ``_``, 表示 Public, 对 API 可见.

除此之外, 还有 ``readonly`` 属性, 如果:

- ``readonly`` 为 ``True`` 则该值不会被 PUT 或者 UPDATE 接口修改.
- ``readonly`` 为 ``False`` 则该值允许被 PUT 或者 UPDATE 接口修改.

.. caution::

    如果一个成员变量是 Private 的, 那么它的 `readonly` 属性则会失效.
