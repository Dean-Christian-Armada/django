# Copyright (c) 2014 Amazon.com, Inc. or its affiliates.  All Rights Reserved
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
from binascii import crc32

try:
    import json
except ImportError:
    import simplejson as json

import boto
from boto.connection import AWSQueryConnection
from boto.regioninfo import RegionInfo
from boto.exception import JSONResponseError
from boto.dynamodb2 import exceptions


class DynamoDBConnection(AWSQueryConnection):
    """
    Amazon DynamoDB **Overview**
    This is the Amazon DynamoDB API Reference. This guide provides
    descriptions and samples of the low-level DynamoDB API. For
    information about DynamoDB application development, go to the
    `Amazon DynamoDB Developer Guide`_.

    Instead of making the requests to the low-level DynamoDB API
    directly from your application, we recommend that you use the AWS
    Software Development Kits (SDKs). The easy-to-use libraries in the
    AWS SDKs make it unnecessary to call the low-level DynamoDB API
    directly from your application. The libraries take care of request
    authentication, serialization, and connection management. For more
    information, go to `Using the AWS SDKs with DynamoDB`_ in the
    Amazon DynamoDB Developer Guide .

    If you decide to code against the low-level DynamoDB API directly,
    you will need to write the necessary code to authenticate your
    requests. For more information on signing your requests, go to
    `Using the DynamoDB API`_ in the Amazon DynamoDB Developer Guide .

    The following are short descriptions of each low-level API action,
    organized by function.

    **Managing Tables**



    + CreateTable - Creates a table with user-specified provisioned
      throughput settings. You must designate one attribute as the hash
      primary key for the table; you can optionally designate a second
      attribute as the range primary key. DynamoDB creates indexes on
      these key attributes for fast data access. Optionally, you can
      create one or more secondary indexes, which provide fast data
      access using non-key attributes.
    + DescribeTable - Returns metadata for a table, such as table
      size, status, and index information.
    + UpdateTable - Modifies the provisioned throughput settings for a
      table. Optionally, you can modify the provisioned throughput
      settings for global secondary indexes on the table.
    + ListTables - Returns a list of all tables associated with the
      current AWS account and endpoint.
    + DeleteTable - Deletes a table and all of its indexes.



    For conceptual information about managing tables, go to `Working
    with Tables`_ in the Amazon DynamoDB Developer Guide .

    **Reading Data**



    + GetItem - Returns a set of attributes for the item that has a
      given primary key. By default, GetItem performs an eventually
      consistent read; however, applications can specify a strongly
      consistent read instead.
    + BatchGetItem - Performs multiple GetItem requests for data items
      using their primary keys, from one table or multiple tables. The
      response from BatchGetItem has a size limit of 1 MB and returns a
      maximum of 100 items. Both eventually consistent and strongly
      consistent reads can be used.
    + Query - Returns one or more items from a table or a secondary
      index. You must provide a specific hash key value. You can narrow
      the scope of the query using comparison operators against a range
      key value, or on the index key. Query supports either eventual or
      strong consistency. A single response has a size limit of 1 MB.
    + Scan - Reads every item in a table; the result set is eventually
      consistent. You can limit the number of items returned by
      filtering the data attributes, using conditional expressions. Scan
      can be used to enable ad-hoc querying of a table against non-key
      attributes; however, since this is a full table scan without using
      an index, Scan should not be used for any application query use
      case that requires predictable performance.



    For conceptual information about reading data, go to `Working with
    Items`_ and `Query and Scan Operations`_ in the Amazon DynamoDB
    Developer Guide .

    **Modifying Data**



    + PutItem - Creates a new item, or replaces an existing item with
      a new item (including all the attributes). By default, if an item
      in the table already exists with the same primary key, the new
      item completely replaces the existing item. You can use
      conditional operators to replace an item only if its attribute
      values match certain conditions, or to insert a new item only if
      that item doesn't already exist.
    + UpdateItem - Modifies the attributes of an existing item. You
      can also use conditional operators to perform an update only if
      the item's attribute values match certain conditions.
    + DeleteItem - Deletes an item in a table by primary key. You can
      use conditional operators to perform a delete an item only if the
      item's attribute values match certain conditions.
    + BatchWriteItem - Performs multiple PutItem and DeleteItem
      requests across multiple tables in a single request. A failure of
      any request(s) in the batch will not cause the entire
      BatchWriteItem operation to fail. Supports batches of up to 25
      items to put or delete, with a maximum total request size of 1 MB.



    For conceptual information about modifying data, go to `Working
    with Items`_ and `Query and Scan Operations`_ in the Amazon
    DynamoDB Developer Guide .
    """
    APIVersion = "2012-08-10"
    DefaultRegionName = "us-east-1"
    DefaultRegionEndpoint = "dynamodb.us-east-1.amazonaws.com"
    ServiceName = "DynamoDB"
    TargetPrefix = "DynamoDB_20120810"
    ResponseError = JSONResponseError

    _faults = {
        "ProvisionedThroughputExceededException": exceptions.ProvisionedThroughputExceededException,
        "LimitExceededException": exceptions.LimitExceededException,
        "ConditionalCheckFailedException": exceptions.ConditionalCheckFailedException,
        "ResourceInUseException": exceptions.ResourceInUseException,
        "ResourceNotFoundException": exceptions.ResourceNotFoundException,
        "InternalServerError": exceptions.InternalServerError,
        "ItemCollectionSizeLimitExceededException": exceptions.ItemCollectionSizeLimitExceededException,
        "ValidationException": exceptions.ValidationException,
    }

    NumberRetries = 10


    def __init__(self, **kwargs):
        region = kwargs.pop('region', None)
        validate_checksums = kwargs.pop('validate_checksums', True)
        if not region:
            region_name = boto.config.get('DynamoDB', 'region',
                                          self.DefaultRegionName)
            for reg in boto.dynamodb2.regions():
                if reg.name == region_name:
                    region = reg
                    break

        # Only set host if it isn't manually overwritten
        if 'host' not in kwargs:
            kwargs['host'] = region.endpoint

        super(DynamoDBConnection, self).__init__(**kwargs)
        self.region = region
        self._validate_checksums = boto.config.getbool(
            'DynamoDB', 'validate_checksums', validate_checksums)
        self.throughput_exceeded_events = 0

    def _required_auth_capability(self):
        return ['hmac-v4']

    def batch_get_item(self, request_items, return_consumed_capacity=None):
        """
        The BatchGetItem operation returns the attributes of one or
        more items from one or more tables. You identify requested
        items by primary key.

        A single operation can retrieve up to 1 MB of data, which can
        contain as many as 100 items. BatchGetItem will return a
        partial result if the response size limit is exceeded, the
        table's provisioned throughput is exceeded, or an internal
        processing failure occurs. If a partial result is returned,
        the operation returns a value for UnprocessedKeys . You can
        use this value to retry the operation starting with the next
        item to get.

        For example, if you ask to retrieve 100 items, but each
        individual item is 50 KB in size, the system returns 20 items
        (1 MB) and an appropriate UnprocessedKeys value so you can get
        the next page of results. If desired, your application can
        include its own logic to assemble the pages of results into
        one dataset.

        If none of the items can be processed due to insufficient
        provisioned throughput on all of the tables in the request,
        then BatchGetItem will throw a
        ProvisionedThroughputExceededException . If at least one of
        the items is successfully processed, then BatchGetItem
        completes successfully, while returning the keys of the unread
        items in UnprocessedKeys .

        If DynamoDB returns any unprocessed items, you should retry
        the batch operation on those items. However, we strongly
        recommend that you use an exponential backoff algorithm . If
        you retry the batch operation immediately, the underlying read
        or write requests can still fail due to throttling on the
        individual tables. If you delay the batch operation using
        exponential backoff, the individual requests in the batch are
        much more likely to succeed.

        For more information, go to `Batch Operations and Error
        Handling`_ in the Amazon DynamoDB Developer Guide.

        By default, BatchGetItem performs eventually consistent reads
        on every table in the request. If you want strongly consistent
        reads instead, you can set ConsistentRead to `True` for any or
        all tables.

        In order to minimize response latency, BatchGetItem retrieves
        items in parallel.

        When designing your application, keep in mind that DynamoDB
        does not return attributes in any particular order. To help
        parse the response by item, include the primary key values for
        the items in your request in the AttributesToGet parameter.

        If a requested item does not exist, it is not returned in the
        result. Requests for nonexistent items consume the minimum
        read capacity units according to the type of read. For more
        information, see `Capacity Units Calculations`_ in the Amazon
        DynamoDB Developer Guide.

        :type request_items: map
        :param request_items:
        A map of one or more table names and, for each table, the corresponding
            primary keys for the items to retrieve. Each table name can be
            invoked only once.

        Each element in the map consists of the following:


        + Keys - An array of primary key attribute values that define specific
              items in the table. For each primary key, you must provide all of
              the key attributes. For example, with a hash type primary key, you
              only need to specify the hash attribute. For a hash-and-range type
              primary key, you must specify both the hash attribute and the range
              attribute.
        + AttributesToGet - One or more attributes to be retrieved from the
              table. By default, all attributes are returned. If a specified
              attribute is not found, it does not appear in the result. Note that
              AttributesToGet has no effect on provisioned throughput
              consumption. DynamoDB determines capacity units consumed based on
              item size, not on the amount of data that is returned to an
              application.
        + ConsistentRead - If `True`, a strongly consistent read is used; if
              `False` (the default), an eventually consistent read is used.

        :type return_consumed_capacity: string
        :param return_consumed_capacity: If set to `TOTAL`, the response
            includes ConsumedCapacity data for tables and indexes. If set to
            `INDEXES`, the response includes ConsumedCapacity for indexes. If
            set to `NONE` (the default), ConsumedCapacity is not included in
            the response.

        """
        params = {'RequestItems': request_items, }
        if return_consumed_capacity is not None:
            params['ReturnConsumedCapacity'] = return_consumed_capacity
        return self.make_request(action='BatchGetItem',
                                 body=json.dumps(params))

    def batch_write_item(self, request_items, return_consumed_capacity=None,
                         return_item_collection_metrics=None):
        """
        The BatchWriteItem operation puts or deletes multiple items in
        one or more tables. A single call to BatchWriteItem can write
        up to 1 MB of data, which can comprise as many as 25 put or
        delete requests. Individual items to be written can be as
        large as 64 KB.

        BatchWriteItem cannot update items. To update items, use the
        UpdateItem API.

        The individual PutItem and DeleteItem operations specified in
        BatchWriteItem are atomic; however BatchWriteItem as a whole
        is not. If any requested operations fail because the table's
        provisioned throughput is exceeded or an internal processing
        failure occurs, the failed operations are returned in the
        UnprocessedItems response parameter. You can investigate and
        optionally resend the requests. Typically, you would call
        BatchWriteItem in a loop. Each iteration would check for
        unprocessed items and submit a new BatchWriteItem request with
        those unprocessed items until all items have been processed.

        Note that if none of the items can be processed due to
        insufficient provisioned throughput on all of the tables in
        the request, then BatchGetItem will throw a
        ProvisionedThroughputExceededException .

        If DynamoDB returns any unprocessed items, you should retry
        the batch operation on those items. However, we strongly
        recommend that you use an exponential backoff algorithm . If
        you retry the batch operation immediately, the underlying read
        or write requests can still fail due to throttling on the
        individual tables. If you delay the batch operation using
        exponential backoff, the individual requests in the batch are
        much more likely to succeed.

        For more information, go to `Batch Operations and Error
        Handling`_ in the Amazon DynamoDB Developer Guide.

        With BatchWriteItem , you can efficiently write or delete
        large amounts of data, such as from Amazon Elastic MapReduce
        (EMR), or copy data from another database into DynamoDB. In
        order to improve performance with these large-scale
        operations, BatchWriteItem does not behave in the same way as
        individual PutItem and DeleteItem calls would For example, you
        cannot specify conditions on individual put and delete
        requests, and BatchWriteItem does not return deleted items in
        the response.

        If you use a programming language that supports concurrency,
        such as Java, you can use threads to write items in parallel.
        Your application must include the necessary logic to manage
        the threads. With languages that don't support threading, such
        as PHP, you must update or delete the specified items one at a
        time. In both situations, BatchWriteItem provides an
        alternative where the API performs the specified put and
        delete operations in parallel, giving you the power of the
        thread pool approach without having to introduce complexity
        into your application.

        Parallel processing reduces latency, but each specified put
        and delete request consumes the same number of write capacity
        units whether it is processed in parallel or not. Delete
        operations on nonexistent items consume one write capacity
        unit.

        If one or more of the following is true, DynamoDB rejects the
        entire batch write operation:


        + One or more tables specified in the BatchWriteItem request
          does not exist.
        + Primary key attributes specified on an item in the request
          do not match those in the corresponding table's primary key
          schema.
        + You try to perform multiple operations on the same item in
          the same BatchWriteItem request. For example, you cannot put
          and delete the same item in the same BatchWriteItem request.
        + The total request size exceeds 1 MB.
        + Any individual item in a batch exceeds 64 KB.

        :type request_items: map
        :param request_items:
        A map of one or more table names and, for each table, a list of
            operations to be performed ( DeleteRequest or PutRequest ). Each
            element in the map consists of the following:


        + DeleteRequest - Perform a DeleteItem operation on the specified item.
              The item to be deleted is identified by a Key subelement:

            + Key - A map of primary key attribute values that uniquely identify
                  the ! item. Each entry in this map consists of an attribute name
                  and an attribute value. For each primary key, you must provide all
                  of the key attributes. For example, with a hash type primary key,
                  you only need to specify the hash attribute. For a hash-and-range
                  type primary key, you must specify both the hash attribute and the
                  range attribute.

        + PutRequest - Perform a PutItem operation on the specified item. The
              item to be put is identified by an Item subelement:

            + Item - A map of attributes and their values. Each entry in this map
                  consists of an attribute name and an attribute value. Attribute
                  values must not be null; string and binary type attributes must
                  have lengths greater than zero; and set type attributes must not be
                  empty. Requests that contain empty values will be rejected with a
                  ValidationException . If you specify any attributes that are part
                  of an index key, then the data types for those attributes must
                  match those of the schema in the table's attribute definition.

        :type return_consumed_capacity: string
        :param return_consumed_capacity: If set to `TOTAL`, the response
            includes ConsumedCapacity data for tables and indexes. If set to
            `INDEXES`, the response includes ConsumedCapacity for indexes. If
            set to `NONE` (the default), ConsumedCapacity is not included in
            the response.

        :type return_item_collection_metrics: string
        :param return_item_collection_metrics: If set to `SIZE`, statistics
            about item collections, if any, that were modified during the
            operation are returned in the response. If set to `NONE` (the
            default), no statistics are returned.

        """
        params = {'RequestItems': request_items, }
        if return_consumed_capacity is not None:
            params['ReturnConsumedCapacity'] = return_consumed_capacity
        if return_item_collection_metrics is not None:
            params['ReturnItemCollectionMetrics'] = return_item_collection_metrics
        return self.make_request(action='BatchWriteItem',
                                 body=json.dumps(params))

    def create_table(self, attribute_definitions, table_name, key_schema,
                     provisioned_throughput, local_secondary_indexes=None,
                     global_secondary_indexes=None):
        """
        The CreateTable operation adds a new table to your account. In
        an AWS account, table names must be unique within each region.
        That is, you can have two tables with same name if you create
        the tables in different regions.

        CreateTable is an asynchronous operation. Upon receiving a
        CreateTable request, DynamoDB immediately returns a response
        with a TableStatus of `CREATING`. After the table is created,
        DynamoDB sets the TableStatus to `ACTIVE`. You can perform
        read and write operations only on an `ACTIVE` table.

        If you want to create multiple tables with secondary indexes
        on them, you must create them sequentially. Only one table
        with secondary indexes can be in the `CREATING` state at any
        given time.

        You can use the DescribeTable API to check the table status.

        :type attribute_definitions: list
        :param attribute_definitions: An array of attributes that describe the
            key schema for the table and indexes.

        :type table_name: string
        :param table_name: The name of the table to create.

        :type key_schema: list
        :param key_schema: Specifies the attributes that make up the primary
            key for a table or an index. The attributes in KeySchema must also
            be defined in the AttributeDefinitions array. For more information,
            see `Data Model`_ in the Amazon DynamoDB Developer Guide.
        Each KeySchemaElement in the array is composed of:


        + AttributeName - The name of this key attribute.
        + KeyType - Determines whether the key attribute is `HASH` or `RANGE`.


        For a primary key that consists of a hash attribute, you must specify
            exactly one element with a KeyType of `HASH`.

        For a primary key that consists of hash and range attributes, you must
            specify exactly two elements, in this order: The first element must
            have a KeyType of `HASH`, and the second element must have a
            KeyType of `RANGE`.

        For more information, see `Specifying the Primary Key`_ in the Amazon
            DynamoDB Developer Guide.

        :type local_secondary_indexes: list
        :param local_secondary_indexes:
        One or more local secondary indexes (the maximum is five) to be created
            on the table. Each index is scoped to a given hash key value. There
            is a 10 GB size limit per hash key; otherwise, the size of a local
            secondary index is unconstrained.

        Each local secondary index in the array includes the following:


        + IndexName - The name of the local secondary index. Must be unique
              only for this table.
        + KeySchema - Specifies the key schema for the local secondary index.
              The key schema must begin with the same hash key attribute as the
              table.
        + Projection - Specifies attributes that are copied (projected) from
              the table into the index. These are in addition to the primary key
              attributes and index key attributes, which are automatically
              projected. Each attribute specification is composed of:

            + ProjectionType - One of the following:

                + `KEYS_ONLY` - Only the index and primary keys are projected into the
                      index.
                + `INCLUDE` - Only the specified table attributes are projected into
                      the index. The list of projected attributes are in NonKeyAttributes
                      .
                + `ALL` - All of the table attributes are projected into the index.

            + NonKeyAttributes - A list of one or more non-key attribute names that
                  are projected into the secondary index. The total count of
                  attributes specified in NonKeyAttributes , summed across all of the
                  secondary indexes, must not exceed 20. If you project the same
                  attribute into two different indexes, this counts as two distinct
                  attributes when determining the total.

        :type global_secondary_indexes: list
        :param global_secondary_indexes:
        One or more global secondary indexes (the maximum is five) to be
            created on the table. Each global secondary index in the array
            includes the following:


        + IndexName - The name of the global secondary index. Must be unique
              only for this table.
        + KeySchema - Specifies the key schema for the global secondary index.
        + Projection - Specifies attributes that are copied (projected) from
              the table into the index. These are in addition to the primary key
              attributes and index key attributes, which are automatically
              projected. Each attribute specification is composed of:

            + ProjectionType - One of the following:

                + `KEYS_ONLY` - Only the index and primary keys are projected into the
                      index.
                + `INCLUDE` - Only the specified table attributes are projected into
                      the index. The list of projected attributes are in NonKeyAttributes
                      .
                + `ALL` - All of the table attributes are projected into the index.

            + NonKeyAttributes - A list of one or more non-key attribute names that
                  are projected into the secondary index. The total count of
                  attributes specified in NonKeyAttributes , summed across all of the
                  secondary indexes, must not exceed 20. If you project the same
                  attribute into two different indexes, this counts as two distinct
                  attributes when determining the total.

        + ProvisionedThroughput - The provisioned throughput settings for the
              global secondary index, consisting of read and write capacity
              units.

        :type provisioned_throughput: dict
        :param provisioned_throughput: Represents the provisioned throughput
            settings for a specified table or index. The settings can be
            modified using the UpdateTable operation.
        For current minimum and maximum provisioned throughput values, see
            `Limits`_ in the Amazon DynamoDB Developer Guide.

        """
        params = {
            'AttributeDefinitions': attribute_definitions,
            'TableName': table_name,
            'KeySchema': key_schema,
            'ProvisionedThroughput': provisioned_throughput,
        }
        if local_secondary_indexes is not None:
            params['LocalSecondaryIndexes'] = local_secondary_indexes
        if global_secondary_indexes is not None:
            params['GlobalSecondaryIndexes'] = global_secondary_indexes
        return self.make_request(action='CreateTable',
                                 body=json.dumps(params))

    def delete_item(self, table_name, key, expected=None,
                    conditional_operator=None, return_values=None,
                    return_consumed_capacity=None,
                    return_item_collection_metrics=None):
        """
        Deletes a single item in a table by primary key. You can
        perform a conditional delete operation that deletes the item
        if it exists, or if it has an expected attribute value.

        In addition to deleting an item, you can also return the
        item's attribute values in the same operation, using the
        ReturnValues parameter.

        Unless you specify conditions, the DeleteItem is an idempotent
        operation; running it multiple times on the same item or
        attribute does not result in an error response.

        Conditional deletes are useful for only deleting items if
        specific conditions are met. If those conditions are met,
        DynamoDB performs the delete. Otherwise, the item is not
        deleted.

        :type table_name: string
        :param table_name: The name of the table from which to delete the item.

        :type key: map
        :param key: A map of attribute names to AttributeValue objects,
            representing the primary key of the item to delete.
        For the primary key, you must provide all of the attributes. For
            example, with a hash type primary key, you only need to specify the
            hash attribute. For a hash-and-range type primary key, you must
            specify both the hash attribute and the range attribute.

        :type expected: map
        :param expected:
        A map of attribute/condition pairs. This is the conditional block for
            the DeleteItem operation.

        Each element of Expected consists of an attribute name, a comparison
            operator, and one or more values. DynamoDB compares the attribute
            with the value(s) you supplied, using the comparison operator. For
            each Expected element, the result of the evaluation is either true
            or false.

        If you specify more than one element in the Expected map, then by
            default all of the conditions must evaluate to true. In other
            words, the conditions are ANDed together. (You can use the
            ConditionalOperator parameter to OR the conditions instead. If you
            do this, then at least one of the conditions must evaluate to true,
            rather than all of them.)

        If the Expected map evaluates to true, then the conditional operation
            succeeds; otherwise, it fails.

        Each item in Expected represents an attribute name for DynamoDB to
            check, along with an AttributeValueList and a ComparisonOperator :


        + AttributeValueList - One or more values to evaluate against the
              supplied attribute. The number of values in the list depends on the
              ComparisonOperator being used. For type Number, value comparisons
              are numeric. String value comparisons for greater than, equals, or
              less than are based on ASCII character code values. For example,
              `a` is greater than `A`, and `aa` is greater than `B`. For a list
              of code values, see
              `http://en.wikipedia.org/wiki/ASCII#ASCII_printable_characters`_.
              For Binary, DynamoDB treats each byte of the binary data as
              unsigned when it compares binary values, for example when
              evaluating query expressions.
        + ComparisonOperator - A comparator for evaluating attributes in the
              AttributeValueList . When performing the comparison, DynamoDB uses
              strongly consistent reads. The following comparison operators are
              available: `EQ | NE | LE | LT | GE | GT | NOT_NULL | NULL |
              CONTAINS | NOT_CONTAINS | BEGINS_WITH | IN | BETWEEN` The following
              are descriptions of each comparison operator.

            + `EQ` : Equal. AttributeValueList can contain only one AttributeValue
                of type String, Number, Binary, String Set, Number Set, or Binary
                Set. If an item contains an AttributeValue of a different type than
                the one specified in the request, the value does not match. For
                example, `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}`
                does not equal `{"NS":["6", "2", "1"]}`. > <li>
            + `NE` : Not equal. AttributeValueList can contain only one
                AttributeValue of type String, Number, Binary, String Set, Number
                Set, or Binary Set. If an item contains an AttributeValue of a
                different type than the one specified in the request, the value
                does not match. For example, `{"S":"6"}` does not equal
                `{"N":"6"}`. Also, `{"N":"6"}` does not equal `{"NS":["6", "2",
                "1"]}`. > <li>
            + `LE` : Less than or equal. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `LT` : Less than. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `GE` : Greater than or equal. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `GT` : Greater than. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `NOT_NULL` : The attribute exists.
            + `NULL` : The attribute does not exist.
            + `CONTAINS` : checks for a subsequence, or value in a set.
                  AttributeValueList can contain only one AttributeValue of type
                  String, Number, or Binary (not a set). If the target attribute of
                  the comparison is a String, then the operation checks for a
                  substring match. If the target attribute of the comparison is
                  Binary, then the operation looks for a subsequence of the target
                  that matches the input. If the target attribute of the comparison
                  is a set ("SS", "NS", or "BS"), then the operation checks for a
                  member of the set (not as a substring).
            + `NOT_CONTAINS` : checks for absence of a subsequence, or absence of a
                  value in a set. AttributeValueList can contain only one
                  AttributeValue of type String, Number, or Binary (not a set). If
                  the target attribute of the comparison is a String, then the
                  operation checks for the absence of a substring match. If the
                  target attribute of the comparison is Binary, then the operation
                  checks for the absence of a subsequence of the target that matches
                  the input. If the target attribute of the comparison is a set
                  ("SS", "NS", or "BS"), then the operation checks for the absence of
                  a member of the set (not as a substring).
            + `BEGINS_WITH` : checks for a prefix. AttributeValueList can contain
                only one AttributeValue of type String or Binary (not a Number or a
                set). The target attribute of the comparison must be a String or
                Binary (not a Number or a set). > <li>
            + `IN` : checks for exact matches. AttributeValueList can contain more
                  than one AttributeValue of type String, Number, or Binary (not a
                  set). The target attribute of the comparison must be of the same
                  type and exact value to match. A String never matches a String set.
            + `BETWEEN` : Greater than or equal to the first value, and less than
                  or equal to the second value. AttributeValueList must contain two
                  AttributeValue elements of the same type, either String, Number, or
                  Binary (not a set). A target attribute matches if the target value
                  is greater than, or equal to, the first element and less than, or
                  equal to, the second element. If an item contains an AttributeValue
                  of a different type than the one specified in the request, the
                  value does not match. For example, `{"S":"6"}` does not compare to
                  `{"N":"6"}`. Also, `{"N":"6"}` does not compare to `{"NS":["6",
                  "2", "1"]}`



        For usage examples of AttributeValueList and ComparisonOperator , see
            `Conditional Expressions`_ in the Amazon DynamoDB Developer Guide.


        For backward compatibility with previous DynamoDB releases, the
            following parameters can be used instead of AttributeValueList and
            ComparisonOperator :


        + Value - A value for DynamoDB to compare with an attribute.
        + Exists - Causes DynamoDB to evaluate the value before attempting the
              conditional operation:

            + If Exists is `True`, DynamoDB will check to see if that attribute
                  value already exists in the table. If it is found, then the
                  condition evaluates to true; otherwise the condition evaluate to
                  false.
            + If Exists is `False`, DynamoDB assumes that the attribute value does
                  not exist in the table. If in fact the value does not exist, then
                  the assumption is valid and the condition evaluates to true. If the
                  value is found, despite the assumption that it does not exist, the
                  condition evaluates to false.



        Even though DynamoDB continues to accept the Value and Exists
            parameters, they are now deprecated. We recommend that you use
            AttributeValueList and ComparisonOperator instead, since they allow
            you to construct a much wider range of conditions.

        The Value and Exists parameters are incompatible with
            AttributeValueList and ComparisonOperator . If you attempt to use
            both sets of parameters at once, DynamoDB will throw a
            ValidationException .

        :type conditional_operator: string
        :param conditional_operator: A logical operator to apply to the
            conditions in the Expected map:

        + `AND` - If all of the conditions evaluate to true, then the entire
              map evaluates to true.
        + `OR` - If at least one of the conditions evaluate to true, then the
              entire map evaluates to true.


        If you omit ConditionalOperator , then `AND` is the default.

        The operation will succeed only if the entire map evaluates to true.

        :type return_values: string
        :param return_values:
        Use ReturnValues if you want to get the item attributes as they
            appeared before they were deleted. For DeleteItem , the valid
            values are:


        + `NONE` - If ReturnValues is not specified, or if its value is `NONE`,
              then nothing is returned. (This is the default for ReturnValues .)
        + `ALL_OLD` - The content of the old item is returned.

        :type return_consumed_capacity: string
        :param return_consumed_capacity: If set to `TOTAL`, the response
            includes ConsumedCapacity data for tables and indexes. If set to
            `INDEXES`, the response includes ConsumedCapacity for indexes. If
            set to `NONE` (the default), ConsumedCapacity is not included in
            the response.

        :type return_item_collection_metrics: string
        :param return_item_collection_metrics: If set to `SIZE`, statistics
            about item collections, if any, that were modified during the
            operation are returned in the response. If set to `NONE` (the
            default), no statistics are returned.

        """
        params = {'TableName': table_name, 'Key': key, }
        if expected is not None:
            params['Expected'] = expected
        if conditional_operator is not None:
            params['ConditionalOperator'] = conditional_operator
        if return_values is not None:
            params['ReturnValues'] = return_values
        if return_consumed_capacity is not None:
            params['ReturnConsumedCapacity'] = return_consumed_capacity
        if return_item_collection_metrics is not None:
            params['ReturnItemCollectionMetrics'] = return_item_collection_metrics
        return self.make_request(action='DeleteItem',
                                 body=json.dumps(params))

    def delete_table(self, table_name):
        """
        The DeleteTable operation deletes a table and all of its
        items. After a DeleteTable request, the specified table is in
        the `DELETING` state until DynamoDB completes the deletion. If
        the table is in the `ACTIVE` state, you can delete it. If a
        table is in `CREATING` or `UPDATING` states, then DynamoDB
        returns a ResourceInUseException . If the specified table does
        not exist, DynamoDB returns a ResourceNotFoundException . If
        table is already in the `DELETING` state, no error is
        returned.

        DynamoDB might continue to accept data read and write
        operations, such as GetItem and PutItem , on a table in the
        `DELETING` state until the table deletion is complete.

        When you delete a table, any indexes on that table are also
        deleted.

        Use the DescribeTable API to check the status of the table.

        :type table_name: string
        :param table_name: The name of the table to delete.

        """
        params = {'TableName': table_name, }
        return self.make_request(action='DeleteTable',
                                 body=json.dumps(params))

    def describe_table(self, table_name):
        """
        Returns information about the table, including the current
        status of the table, when it was created, the primary key
        schema, and any indexes on the table.

        :type table_name: string
        :param table_name: The name of the table to describe.

        """
        params = {'TableName': table_name, }
        return self.make_request(action='DescribeTable',
                                 body=json.dumps(params))

    def get_item(self, table_name, key, attributes_to_get=None,
                 consistent_read=None, return_consumed_capacity=None):
        """
        The GetItem operation returns a set of attributes for the item
        with the given primary key. If there is no matching item,
        GetItem does not return any data.

        GetItem provides an eventually consistent read by default. If
        your application requires a strongly consistent read, set
        ConsistentRead to `True`. Although a strongly consistent read
        might take more time than an eventually consistent read, it
        always returns the last updated value.

        :type table_name: string
        :param table_name: The name of the table containing the requested item.

        :type key: map
        :param key: A map of attribute names to AttributeValue objects,
            representing the primary key of the item to retrieve.
        For the primary key, you must provide all of the attributes. For
            example, with a hash type primary key, you only need to specify the
            hash attribute. For a hash-and-range type primary key, you must
            specify both the hash attribute and the range attribute.

        :type attributes_to_get: list
        :param attributes_to_get: The names of one or more attributes to
            retrieve. If no attribute names are specified, then all attributes
            will be returned. If any of the requested attributes are not found,
            they will not appear in the result.
        Note that AttributesToGet has no effect on provisioned throughput
            consumption. DynamoDB determines capacity units consumed based on
            item size, not on the amount of data that is returned to an
            application.

        :type consistent_read: boolean
        :param consistent_read: If set to `True`, then the operation uses
            strongly consistent reads; otherwise, eventually consistent reads
            are used.

        :type return_consumed_capacity: string
        :param return_consumed_capacity: If set to `TOTAL`, the response
            includes ConsumedCapacity data for tables and indexes. If set to
            `INDEXES`, the response includes ConsumedCapacity for indexes. If
            set to `NONE` (the default), ConsumedCapacity is not included in
            the response.

        """
        params = {'TableName': table_name, 'Key': key, }
        if attributes_to_get is not None:
            params['AttributesToGet'] = attributes_to_get
        if consistent_read is not None:
            params['ConsistentRead'] = consistent_read
        if return_consumed_capacity is not None:
            params['ReturnConsumedCapacity'] = return_consumed_capacity
        return self.make_request(action='GetItem',
                                 body=json.dumps(params))

    def list_tables(self, exclusive_start_table_name=None, limit=None):
        """
        Returns an array of table names associated with the current
        account and endpoint. The output from ListTables is paginated,
        with each page returning a maximum of 100 table names.

        :type exclusive_start_table_name: string
        :param exclusive_start_table_name: The first table name that this
            operation will evaluate. Use the value that was returned for
            LastEvaluatedTableName in a previous operation, so that you can
            obtain the next page of results.

        :type limit: integer
        :param limit: A maximum number of table names to return. If this
            parameter is not specified, the limit is 100.

        """
        params = {}
        if exclusive_start_table_name is not None:
            params['ExclusiveStartTableName'] = exclusive_start_table_name
        if limit is not None:
            params['Limit'] = limit
        return self.make_request(action='ListTables',
                                 body=json.dumps(params))

    def put_item(self, table_name, item, expected=None, return_values=None,
                 return_consumed_capacity=None,
                 return_item_collection_metrics=None,
                 conditional_operator=None):
        """
        Creates a new item, or replaces an old item with a new item.
        If an item already exists in the specified table with the same
        primary key, the new item completely replaces the existing
        item. You can perform a conditional put (insert a new item if
        one with the specified primary key doesn't exist), or replace
        an existing item if it has certain attribute values.

        In addition to putting an item, you can also return the item's
        attribute values in the same operation, using the ReturnValues
        parameter.

        When you add an item, the primary key attribute(s) are the
        only required attributes. Attribute values cannot be null.
        String and binary type attributes must have lengths greater
        than zero. Set type attributes cannot be empty. Requests with
        empty values will be rejected with a ValidationException .

        You can request that PutItem return either a copy of the old
        item (before the update) or a copy of the new item (after the
        update). For more information, see the ReturnValues
        description.

        To prevent a new item from replacing an existing item, use a
        conditional put operation with ComparisonOperator set to
        `NULL` for the primary key attribute, or attributes.

        For more information about using this API, see `Working with
        Items`_ in the Amazon DynamoDB Developer Guide.

        :type table_name: string
        :param table_name: The name of the table to contain the item.

        :type item: map
        :param item: A map of attribute name/value pairs, one for each
            attribute. Only the primary key attributes are required; you can
            optionally provide other attribute name-value pairs for the item.
        You must provide all of the attributes for the primary key. For
            example, with a hash type primary key, you only need to specify the
            hash attribute. For a hash-and-range type primary key, you must
            specify both the hash attribute and the range attribute.

        If you specify any attributes that are part of an index key, then the
            data types for those attributes must match those of the schema in
            the table's attribute definition.

        For more information about primary keys, see `Primary Key`_ in the
            Amazon DynamoDB Developer Guide.

        Each element in the Item map is an AttributeValue object.

        :type expected: map
        :param expected:
        A map of attribute/condition pairs. This is the conditional block for
            the PutItem operation.

        Each element of Expected consists of an attribute name, a comparison
            operator, and one or more values. DynamoDB compares the attribute
            with the value(s) you supplied, using the comparison operator. For
            each Expected element, the result of the evaluation is either true
            or false.

        If you specify more than one element in the Expected map, then by
            default all of the conditions must evaluate to true. In other
            words, the conditions are ANDed together. (You can use the
            ConditionalOperator parameter to OR the conditions instead. If you
            do this, then at least one of the conditions must evaluate to true,
            rather than all of them.)

        If the Expected map evaluates to true, then the conditional operation
            succeeds; otherwise, it fails.

        Each item in Expected represents an attribute name for DynamoDB to
            check, along with an AttributeValueList and a ComparisonOperator :


        + AttributeValueList - One or more values to evaluate against the
              supplied attribute. The number of values in the list depends on the
              ComparisonOperator being used. For type Number, value comparisons
              are numeric. String value comparisons for greater than, equals, or
              less than are based on ASCII character code values. For example,
              `a` is greater than `A`, and `aa` is greater than `B`. For a list
              of code values, see
              `http://en.wikipedia.org/wiki/ASCII#ASCII_printable_characters`_.
              For Binary, DynamoDB treats each byte of the binary data as
              unsigned when it compares binary values, for example when
              evaluating query expressions.
        + ComparisonOperator - A comparator for evaluating attributes in the
              AttributeValueList . When performing the comparison, DynamoDB uses
              strongly consistent reads. The following comparison operators are
              available: `EQ | NE | LE | LT | GE | GT | NOT_NULL | NULL |
              CONTAINS | NOT_CONTAINS | BEGINS_WITH | IN | BETWEEN` The following
              are descriptions of each comparison operator.

            + `EQ` : Equal. AttributeValueList can contain only one AttributeValue
                of type String, Number, Binary, String Set, Number Set, or Binary
                Set. If an item contains an AttributeValue of a different type than
                the one specified in the request, the value does not match. For
                example, `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}`
                does not equal `{"NS":["6", "2", "1"]}`. > <li>
            + `NE` : Not equal. AttributeValueList can contain only one
                AttributeValue of type String, Number, Binary, String Set, Number
                Set, or Binary Set. If an item contains an AttributeValue of a
                different type than the one specified in the request, the value
                does not match. For example, `{"S":"6"}` does not equal
                `{"N":"6"}`. Also, `{"N":"6"}` does not equal `{"NS":["6", "2",
                "1"]}`. > <li>
            + `LE` : Less than or equal. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `LT` : Less than. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `GE` : Greater than or equal. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `GT` : Greater than. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `NOT_NULL` : The attribute exists.
            + `NULL` : The attribute does not exist.
            + `CONTAINS` : checks for a subsequence, or value in a set.
                  AttributeValueList can contain only one AttributeValue of type
                  String, Number, or Binary (not a set). If the target attribute of
                  the comparison is a String, then the operation checks for a
                  substring match. If the target attribute of the comparison is
                  Binary, then the operation looks for a subsequence of the target
                  that matches the input. If the target attribute of the comparison
                  is a set ("SS", "NS", or "BS"), then the operation checks for a
                  member of the set (not as a substring).
            + `NOT_CONTAINS` : checks for absence of a subsequence, or absence of a
                  value in a set. AttributeValueList can contain only one
                  AttributeValue of type String, Number, or Binary (not a set). If
                  the target attribute of the comparison is a String, then the
                  operation checks for the absence of a substring match. If the
                  target attribute of the comparison is Binary, then the operation
                  checks for the absence of a subsequence of the target that matches
                  the input. If the target attribute of the comparison is a set
                  ("SS", "NS", or "BS"), then the operation checks for the absence of
                  a member of the set (not as a substring).
            + `BEGINS_WITH` : checks for a prefix. AttributeValueList can contain
                only one AttributeValue of type String or Binary (not a Number or a
                set). The target attribute of the comparison must be a String or
                Binary (not a Number or a set). > <li>
            + `IN` : checks for exact matches. AttributeValueList can contain more
                  than one AttributeValue of type String, Number, or Binary (not a
                  set). The target attribute of the comparison must be of the same
                  type and exact value to match. A String never matches a String set.
            + `BETWEEN` : Greater than or equal to the first value, and less than
                  or equal to the second value. AttributeValueList must contain two
                  AttributeValue elements of the same type, either String, Number, or
                  Binary (not a set). A target attribute matches if the target value
                  is greater than, or equal to, the first element and less than, or
                  equal to, the second element. If an item contains an AttributeValue
                  of a different type than the one specified in the request, the
                  value does not match. For example, `{"S":"6"}` does not compare to
                  `{"N":"6"}`. Also, `{"N":"6"}` does not compare to `{"NS":["6",
                  "2", "1"]}`



        For usage examples of AttributeValueList and ComparisonOperator , see
            `Conditional Expressions`_ in the Amazon DynamoDB Developer Guide.


        For backward compatibility with previous DynamoDB releases, the
            following parameters can be used instead of AttributeValueList and
            ComparisonOperator :


        + Value - A value for DynamoDB to compare with an attribute.
        + Exists - Causes DynamoDB to evaluate the value before attempting the
              conditional operation:

            + If Exists is `True`, DynamoDB will check to see if that attribute
                  value already exists in the table. If it is found, then the
                  condition evaluates to true; otherwise the condition evaluate to
                  false.
            + If Exists is `False`, DynamoDB assumes that the attribute value does
                  not exist in the table. If in fact the value does not exist, then
                  the assumption is valid and the condition evaluates to true. If the
                  value is found, despite the assumption that it does not exist, the
                  condition evaluates to false.



        Even though DynamoDB continues to accept the Value and Exists
            parameters, they are now deprecated. We recommend that you use
            AttributeValueList and ComparisonOperator instead, since they allow
            you to construct a much wider range of conditions.

        The Value and Exists parameters are incompatible with
            AttributeValueList and ComparisonOperator . If you attempt to use
            both sets of parameters at once, DynamoDB will throw a
            ValidationException .

        :type return_values: string
        :param return_values:
        Use ReturnValues if you want to get the item attributes as they
            appeared before they were updated with the PutItem request. For
            PutItem , the valid values are:


        + `NONE` - If ReturnValues is not specified, or if its value is `NONE`,
              then nothing is returned. (This is the default for ReturnValues .)
        + `ALL_OLD` - If PutItem overwrote an attribute name-value pair, then
              the content of the old item is returned.

        :type return_consumed_capacity: string
        :param return_consumed_capacity: If set to `TOTAL`, the response
            includes ConsumedCapacity data for tables and indexes. If set to
            `INDEXES`, the response includes ConsumedCapacity for indexes. If
            set to `NONE` (the default), ConsumedCapacity is not included in
            the response.

        :type return_item_collection_metrics: string
        :param return_item_collection_metrics: If set to `SIZE`, statistics
            about item collections, if any, that were modified during the
            operation are returned in the response. If set to `NONE` (the
            default), no statistics are returned.

        :type conditional_operator: string
        :param conditional_operator: A logical operator to apply to the
            conditions in the Expected map:

        + `AND` - If all of the conditions evaluate to true, then the entire
              map evaluates to true.
        + `OR` - If at least one of the conditions evaluate to true, then the
              entire map evaluates to true.


        If you omit ConditionalOperator , then `AND` is the default.

        The operation will succeed only if the entire map evaluates to true.

        """
        params = {'TableName': table_name, 'Item': item, }
        if expected is not None:
            params['Expected'] = expected
        if return_values is not None:
            params['ReturnValues'] = return_values
        if return_consumed_capacity is not None:
            params['ReturnConsumedCapacity'] = return_consumed_capacity
        if return_item_collection_metrics is not None:
            params['ReturnItemCollectionMetrics'] = return_item_collection_metrics
        if conditional_operator is not None:
            params['ConditionalOperator'] = conditional_operator
        return self.make_request(action='PutItem',
                                 body=json.dumps(params))

    def query(self, table_name, key_conditions, index_name=None, select=None,
              attributes_to_get=None, limit=None, consistent_read=None,
              query_filter=None, conditional_operator=None,
              scan_index_forward=None, exclusive_start_key=None,
              return_consumed_capacity=None):
        """
        A Query operation directly accesses items from a table using
        the table primary key, or from an index using the index key.
        You must provide a specific hash key value. You can narrow the
        scope of the query by using comparison operators on the range
        key value, or on the index key. You can use the
        ScanIndexForward parameter to get results in forward or
        reverse order, by range key or by index key.

        Queries that do not return results consume the minimum read
        capacity units according to the type of read.

        If the total number of items meeting the query criteria
        exceeds the result set size limit of 1 MB, the query stops and
        results are returned to the user with a LastEvaluatedKey to
        continue the query in a subsequent operation. Unlike a Scan
        operation, a Query operation never returns an empty result set
        and a LastEvaluatedKey . The LastEvaluatedKey is only provided
        if the results exceed 1 MB, or if you have used Limit .

        You can query a table, a local secondary index, or a global
        secondary index. For a query on a table or on a local
        secondary index, you can set ConsistentRead to true and obtain
        a strongly consistent result. Global secondary indexes support
        eventually consistent reads only, so do not specify
        ConsistentRead when querying a global secondary index.

        :type table_name: string
        :param table_name: The name of the table containing the requested
            items.

        :type index_name: string
        :param index_name: The name of an index to query. This can be any local
            secondary index or global secondary index on the table.

        :type select: string
        :param select: The attributes to be returned in the result. You can
            retrieve all item attributes, specific item attributes, the count
            of matching items, or in the case of an index, some or all of the
            attributes projected into the index.

        + `ALL_ATTRIBUTES`: Returns all of the item attributes from the
              specified table or index. If you are querying a local secondary
              index, then for each matching item in the index DynamoDB will fetch
              the entire item from the parent table. If the index is configured
              to project all item attributes, then all of the data can be
              obtained from the local secondary index, and no fetching is
              required..
        + `ALL_PROJECTED_ATTRIBUTES`: Allowed only when querying an index.
              Retrieves all attributes which have been projected into the index.
              If the index is configured to project all attributes, this is
              equivalent to specifying `ALL_ATTRIBUTES`.
        + `COUNT`: Returns the number of matching items, rather than the
              matching items themselves.
        + `SPECIFIC_ATTRIBUTES` : Returns only the attributes listed in
              AttributesToGet . This is equivalent to specifying AttributesToGet
              without specifying any value for Select . If you are querying a
              local secondary index and request only attributes that are
              projected into that index, the operation will read only the index
              and not the table. If any of the requested attributes are not
              projected into the local secondary index, DynamoDB will fetch each
              of these attributes from the parent table. This extra fetching
              incurs additional throughput cost and latency. If you are querying
              a global secondary index, you can only request attributes that are
              projected into the index. Global secondary index queries cannot
              fetch attributes from the parent table.


        If neither Select nor AttributesToGet are specified, DynamoDB defaults
            to `ALL_ATTRIBUTES` when accessing a table, and
            `ALL_PROJECTED_ATTRIBUTES` when accessing an index. You cannot use
            both Select and AttributesToGet together in a single request,
            unless the value for Select is `SPECIFIC_ATTRIBUTES`. (This usage
            is equivalent to specifying AttributesToGet without any value for
            Select .)

        :type attributes_to_get: list
        :param attributes_to_get: The names of one or more attributes to
            retrieve. If no attribute names are specified, then all attributes
            will be returned. If any of the requested attributes are not found,
            they will not appear in the result.
        Note that AttributesToGet has no effect on provisioned throughput
            consumption. DynamoDB determines capacity units consumed based on
            item size, not on the amount of data that is returned to an
            application.

        You cannot use both AttributesToGet and Select together in a Query
            request, unless the value for Select is `SPECIFIC_ATTRIBUTES`.
            (This usage is equivalent to specifying AttributesToGet without any
            value for Select .)

        If you are querying a local secondary index and request only attributes
            that are projected into that index, the operation will read only
            the index and not the table. If any of the requested attributes are
            not projected into the local secondary index, DynamoDB will fetch
            each of these attributes from the parent table. This extra fetching
            incurs additional throughput cost and latency.

        If you are querying a global secondary index, you can only request
            attributes that are projected into the index. Global secondary
            index queries cannot fetch attributes from the parent table.

        :type limit: integer
        :param limit: The maximum number of items to evaluate (not necessarily
            the number of matching items). If DynamoDB processes the number of
            items up to the limit while processing the results, it stops the
            operation and returns the matching values up to that point, and a
            LastEvaluatedKey to apply in a subsequent operation, so that you
            can pick up where you left off. Also, if the processed data set
            size exceeds 1 MB before DynamoDB reaches this limit, it stops the
            operation and returns the matching values up to the limit, and a
            LastEvaluatedKey to apply in a subsequent operation to continue the
            operation. For more information, see `Query and Scan`_ in the
            Amazon DynamoDB Developer Guide.

        :type consistent_read: boolean
        :param consistent_read: If set to `True`, then the operation uses
            strongly consistent reads; otherwise, eventually consistent reads
            are used.
        Strongly consistent reads are not supported on global secondary
            indexes. If you query a global secondary index with ConsistentRead
            set to `True`, you will receive an error message.

        :type key_conditions: map
        :param key_conditions: The selection criteria for the query.
        For a query on a table, you can only have conditions on the table
            primary key attributes. You must specify the hash key attribute
            name and value as an `EQ` condition. You can optionally specify a
            second condition, referring to the range key attribute.

        For a query on an index, you can only have conditions on the index key
            attributes. You must specify the index hash attribute name and
            value as an EQ condition. You can optionally specify a second
            condition, referring to the index key range attribute.

        If you specify more than one condition in the KeyConditions map, then
            by default all of the conditions must evaluate to true. In other
            words, the conditions are ANDed together. (You can use the
            ConditionalOperator parameter to OR the conditions instead. If you
            do this, then at least one of the conditions must evaluate to true,
            rather than all of them.)

        Each KeyConditions element consists of an attribute name to compare,
            along with the following:


        + AttributeValueList - One or more values to evaluate against the
              supplied attribute. The number of values in the list depends on the
              ComparisonOperator being used. For type Number, value comparisons
              are numeric. String value comparisons for greater than, equals, or
              less than are based on ASCII character code values. For example,
              `a` is greater than `A`, and `aa` is greater than `B`. For a list
              of code values, see
              `http://en.wikipedia.org/wiki/ASCII#ASCII_printable_characters`_.
              For Binary, DynamoDB treats each byte of the binary data as
              unsigned when it compares binary values, for example when
              evaluating query expressions.
        + ComparisonOperator - A comparator for evaluating attributes. For
              example, equals, greater than, less than, etc. For KeyConditions ,
              only the following comparison operators are supported: `EQ | LE |
              LT | GE | GT | BEGINS_WITH | BETWEEN` The following are
              descriptions of these comparison operators.

            + `EQ` : Equal. AttributeValueList can contain only one AttributeValue
                  of type String, Number, or Binary (not a set). If an item contains
                  an AttributeValue of a different type than the one specified in the
                  request, the value does not match. For example, `{"S":"6"}` does
                  not equal `{"N":"6"}`. Also, `{"N":"6"}` does not equal
                  `{"NS":["6", "2", "1"]}`.
            + `LE` : Less than or equal. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `LT` : Less than. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `GE` : Greater than or equal. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `GT` : Greater than. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `BEGINS_WITH` : checks for a prefix. AttributeValueList can contain
                only one AttributeValue of type String or Binary (not a Number or a
                set). The target attribute of the comparison must be a String or
                Binary (not a Number or a set). > <li>
            + `BETWEEN` : Greater than or equal to the first value, and less than
                  or equal to the second value. AttributeValueList must contain two
                  AttributeValue elements of the same type, either String, Number, or
                  Binary (not a set). A target attribute matches if the target value
                  is greater than, or equal to, the first element and less than, or
                  equal to, the second element. If an item contains an AttributeValue
                  of a different type than the one specified in the request, the
                  value does not match. For example, `{"S":"6"}` does not compare to
                  `{"N":"6"}`. Also, `{"N":"6"}` does not compare to `{"NS":["6",
                  "2", "1"]}`



        For usage examples of AttributeValueList and ComparisonOperator , see
            `Conditional Expressions`_ in the Amazon DynamoDB Developer Guide.

        :type query_filter: map
        :param query_filter:
        Evaluates the query results and returns only the desired values.

        If you specify more than one condition in the QueryFilter map, then by
            default all of the conditions must evaluate to true. In other
            words, the conditions are ANDed together. (You can use the
            ConditionalOperator parameter to OR the conditions instead. If you
            do this, then at least one of the conditions must evaluate to true,
            rather than all of them.)

        Each QueryFilter element consists of an attribute name to compare,
            along with the following:


        + AttributeValueList - One or more values to evaluate against the
              supplied attribute. The number of values in the list depends on the
              ComparisonOperator being used. For type Number, value comparisons
              are numeric. String value comparisons for greater than, equals, or
              less than are based on ASCII character code values. For example,
              `a` is greater than `A`, and `aa` is greater than `B`. For a list
              of code values, see
              `http://en.wikipedia.org/wiki/ASCII#ASCII_printable_characters`_.
              For Binary, DynamoDB treats each byte of the binary data as
              unsigned when it compares binary values, for example when
              evaluating query expressions. For information on specifying data
              types in JSON, see `JSON Data Format`_ in the Amazon DynamoDB
              Developer Guide.
        + ComparisonOperator - A comparator for evaluating attributes. For
              example, equals, greater than, less than, etc. The following
              comparison operators are available: `EQ | NE | LE | LT | GE | GT |
              NOT_NULL | NULL | CONTAINS | NOT_CONTAINS | BEGINS_WITH | IN |
              BETWEEN` For complete descriptions of all comparison operators, see
              `API_Condition.html`_.

        :type conditional_operator: string
        :param conditional_operator: A logical operator to apply to the
            conditions in the QueryFilter map:

        + `AND` - If all of the conditions evaluate to true, then the entire
              map evaluates to true.
        + `OR` - If at least one of the conditions evaluate to true, then the
              entire map evaluates to true.


        If you omit ConditionalOperator , then `AND` is the default.

        The operation will succeed only if the entire map evaluates to true.

        :type scan_index_forward: boolean
        :param scan_index_forward: Specifies ascending (true) or descending
            (false) traversal of the index. DynamoDB returns results reflecting
            the requested order determined by the range key. If the data type
            is Number, the results are returned in numeric order. For String,
            the results are returned in order of ASCII character code values.
            For Binary, DynamoDB treats each byte of the binary data as
            unsigned when it compares binary values.
        If ScanIndexForward is not specified, the results are returned in
            ascending order.

        :type exclusive_start_key: map
        :param exclusive_start_key: The primary key of the first item that this
            operation will evaluate. Use the value that was returned for
            LastEvaluatedKey in the previous operation.
        The data type for ExclusiveStartKey must be String, Number or Binary.
            No set data types are allowed.

        :type return_consumed_capacity: string
        :param return_consumed_capacity: If set to `TOTAL`, the response
            includes ConsumedCapacity data for tables and indexes. If set to
            `INDEXES`, the response includes ConsumedCapacity for indexes. If
            set to `NONE` (the default), ConsumedCapacity is not included in
            the response.

        """
        params = {
            'TableName': table_name,
            'KeyConditions': key_conditions,
        }
        if index_name is not None:
            params['IndexName'] = index_name
        if select is not None:
            params['Select'] = select
        if attributes_to_get is not None:
            params['AttributesToGet'] = attributes_to_get
        if limit is not None:
            params['Limit'] = limit
        if consistent_read is not None:
            params['ConsistentRead'] = consistent_read
        if query_filter is not None:
            params['QueryFilter'] = query_filter
        if conditional_operator is not None:
            params['ConditionalOperator'] = conditional_operator
        if scan_index_forward is not None:
            params['ScanIndexForward'] = scan_index_forward
        if exclusive_start_key is not None:
            params['ExclusiveStartKey'] = exclusive_start_key
        if return_consumed_capacity is not None:
            params['ReturnConsumedCapacity'] = return_consumed_capacity
        return self.make_request(action='Query',
                                 body=json.dumps(params))

    def scan(self, table_name, attributes_to_get=None, limit=None,
             select=None, scan_filter=None, conditional_operator=None,
             exclusive_start_key=None, return_consumed_capacity=None,
             total_segments=None, segment=None):
        """
        The Scan operation returns one or more items and item
        attributes by accessing every item in the table. To have
        DynamoDB return fewer items, you can provide a ScanFilter .

        If the total number of scanned items exceeds the maximum data
        set size limit of 1 MB, the scan stops and results are
        returned to the user with a LastEvaluatedKey to continue the
        scan in a subsequent operation. The results also include the
        number of items exceeding the limit. A scan can result in no
        table data meeting the filter criteria.

        The result set is eventually consistent.

        By default, Scan operations proceed sequentially; however, for
        faster performance on large tables, applications can request a
        parallel Scan by specifying the Segment and TotalSegments
        parameters. For more information, see `Parallel Scan`_ in the
        Amazon DynamoDB Developer Guide.

        :type table_name: string
        :param table_name: The name of the table containing the requested
            items.

        :type attributes_to_get: list
        :param attributes_to_get: The names of one or more attributes to
            retrieve. If no attribute names are specified, then all attributes
            will be returned. If any of the requested attributes are not found,
            they will not appear in the result.
        Note that AttributesToGet has no effect on provisioned throughput
            consumption. DynamoDB determines capacity units consumed based on
            item size, not on the amount of data that is returned to an
            application.

        :type limit: integer
        :param limit: The maximum number of items to evaluate (not necessarily
            the number of matching items). If DynamoDB processes the number of
            items up to the limit while processing the results, it stops the
            operation and returns the matching values up to that point, and a
            LastEvaluatedKey to apply in a subsequent operation, so that you
            can pick up where you left off. Also, if the processed data set
            size exceeds 1 MB before DynamoDB reaches this limit, it stops the
            operation and returns the matching values up to the limit, and a
            LastEvaluatedKey to apply in a subsequent operation to continue the
            operation. For more information, see `Query and Scan`_ in the
            Amazon DynamoDB Developer Guide.

        :type select: string
        :param select: The attributes to be returned in the result. You can
            retrieve all item attributes, specific item attributes, or the
            count of matching items.

        + `ALL_ATTRIBUTES`: Returns all of the item attributes.
        + `COUNT`: Returns the number of matching items, rather than the
              matching items themselves.
        + `SPECIFIC_ATTRIBUTES` : Returns only the attributes listed in
              AttributesToGet . This is equivalent to specifying AttributesToGet
              without specifying any value for Select .


        If neither Select nor AttributesToGet are specified, DynamoDB defaults
            to `ALL_ATTRIBUTES`. You cannot use both Select and AttributesToGet
            together in a single request, unless the value for Select is
            `SPECIFIC_ATTRIBUTES`. (This usage is equivalent to specifying
            AttributesToGet without any value for Select .)

        :type scan_filter: map
        :param scan_filter:
        Evaluates the scan results and returns only the desired values.

        If you specify more than one condition in the ScanFilter map, then by
            default all of the conditions must evaluate to true. In other
            words, the conditions are ANDed together. (You can use the
            ConditionalOperator parameter to OR the conditions instead. If you
            do this, then at least one of the conditions must evaluate to true,
            rather than all of them.)

        Each ScanFilter element consists of an attribute name to compare, along
            with the following:


        + AttributeValueList - One or more values to evaluate against the
              supplied attribute. The number of values in the list depends on the
              ComparisonOperator being used. For type Number, value comparisons
              are numeric. String value comparisons for greater than, equals, or
              less than are based on ASCII character code values. For example,
              `a` is greater than `A`, and `aa` is greater than `B`. For a list
              of code values, see
              `http://en.wikipedia.org/wiki/ASCII#ASCII_printable_characters`_.
              For Binary, DynamoDB treats each byte of the binary data as
              unsigned when it compares binary values, for example when
              evaluating query expressions. For information on specifying data
              types in JSON, see `JSON Data Format`_ in the Amazon DynamoDB
              Developer Guide.
        + ComparisonOperator - A comparator for evaluating attributes. For
              example, equals, greater than, less than, etc. The following
              comparison operators are available: `EQ | NE | LE | LT | GE | GT |
              NOT_NULL | NULL | CONTAINS | NOT_CONTAINS | BEGINS_WITH | IN |
              BETWEEN` For complete descriptions of all comparison operators, see
              `Condition`_.

        :type conditional_operator: string
        :param conditional_operator: A logical operator to apply to the
            conditions in the ScanFilter map:

        + `AND` - If all of the conditions evaluate to true, then the entire
              map evaluates to true.
        + `OR` - If at least one of the conditions evaluate to true, then the
              entire map evaluates to true.


        If you omit ConditionalOperator , then `AND` is the default.

        The operation will succeed only if the entire map evaluates to true.

        :type exclusive_start_key: map
        :param exclusive_start_key: The primary key of the first item that this
            operation will evaluate. Use the value that was returned for
            LastEvaluatedKey in the previous operation.
        The data type for ExclusiveStartKey must be String, Number or Binary.
            No set data types are allowed.

        In a parallel scan, a Scan request that includes ExclusiveStartKey must
            specify the same segment whose previous Scan returned the
            corresponding value of LastEvaluatedKey .

        :type return_consumed_capacity: string
        :param return_consumed_capacity: If set to `TOTAL`, the response
            includes ConsumedCapacity data for tables and indexes. If set to
            `INDEXES`, the response includes ConsumedCapacity for indexes. If
            set to `NONE` (the default), ConsumedCapacity is not included in
            the response.

        :type total_segments: integer
        :param total_segments: For a parallel Scan request, TotalSegments
            represents the total number of segments into which the Scan
            operation will be divided. The value of TotalSegments corresponds
            to the number of application workers that will perform the parallel
            scan. For example, if you want to scan a table using four
            application threads, you would specify a TotalSegments value of 4.
        The value for TotalSegments must be greater than or equal to 1, and
            less than or equal to 4096. If you specify a TotalSegments value of
            1, the Scan will be sequential rather than parallel.

        If you specify TotalSegments , you must also specify Segment .

        :type segment: integer
        :param segment: For a parallel Scan request, Segment identifies an
            individual segment to be scanned by an application worker.
        Segment IDs are zero-based, so the first segment is always 0. For
            example, if you want to scan a table using four application
            threads, the first thread would specify a Segment value of 0, the
            second thread would specify 1, and so on.

        The value of LastEvaluatedKey returned from a parallel Scan request
            must be used as ExclusiveStartKey with the same Segment ID in a
            subsequent Scan operation.

        The value for Segment must be greater than or equal to 0, and less than
            the value provided for TotalSegments .

        If you specify Segment , you must also specify TotalSegments .

        """
        params = {'TableName': table_name, }
        if attributes_to_get is not None:
            params['AttributesToGet'] = attributes_to_get
        if limit is not None:
            params['Limit'] = limit
        if select is not None:
            params['Select'] = select
        if scan_filter is not None:
            params['ScanFilter'] = scan_filter
        if conditional_operator is not None:
            params['ConditionalOperator'] = conditional_operator
        if exclusive_start_key is not None:
            params['ExclusiveStartKey'] = exclusive_start_key
        if return_consumed_capacity is not None:
            params['ReturnConsumedCapacity'] = return_consumed_capacity
        if total_segments is not None:
            params['TotalSegments'] = total_segments
        if segment is not None:
            params['Segment'] = segment
        return self.make_request(action='Scan',
                                 body=json.dumps(params))

    def update_item(self, table_name, key, attribute_updates=None,
                    expected=None, conditional_operator=None,
                    return_values=None, return_consumed_capacity=None,
                    return_item_collection_metrics=None):
        """
        Edits an existing item's attributes, or inserts a new item if
        it does not already exist. You can put, delete, or add
        attribute values. You can also perform a conditional update
        (insert a new attribute name-value pair if it doesn't exist,
        or replace an existing name-value pair if it has certain
        expected attribute values).

        In addition to updating an item, you can also return the
        item's attribute values in the same operation, using the
        ReturnValues parameter.

        :type table_name: string
        :param table_name: The name of the table containing the item to update.

        :type key: map
        :param key: The primary key of the item to be updated. Each element
            consists of an attribute name and a value for that attribute.
        For the primary key, you must provide all of the attributes. For
            example, with a hash type primary key, you only need to specify the
            hash attribute. For a hash-and-range type primary key, you must
            specify both the hash attribute and the range attribute.

        :type attribute_updates: map
        :param attribute_updates: The names of attributes to be modified, the
            action to perform on each, and the new value for each. If you are
            updating an attribute that is an index key attribute for any
            indexes on that table, the attribute type must match the index key
            type defined in the AttributesDefinition of the table description.
            You can use UpdateItem to update any non-key attributes.
        Attribute values cannot be null. String and binary type attributes must
            have lengths greater than zero. Set type attributes must not be
            empty. Requests with empty values will be rejected with a
            ValidationException .

        Each AttributeUpdates element consists of an attribute name to modify,
            along with the following:


        + Value - The new value, if applicable, for this attribute.
        + Action - Specifies how to perform the update. Valid values for Action
              are `PUT`, `DELETE`, and `ADD`. The behavior depends on whether the
              specified primary key already exists in the table. **If an item
              with the specified Key is found in the table:**

            + `PUT` - Adds the specified attribute to the item. If the attribute
                  already exists, it is replaced by the new value.
            + `DELETE` - If no value is specified, the attribute and its value are
                  removed from the item. The data type of the specified value must
                  match the existing value's data type. If a set of values is
                  specified, then those values are subtracted from the old set. For
                  example, if the attribute value was the set `[a,b,c]` and the
                  DELETE action specified `[a,c]`, then the final attribute value
                  would be `[b]`. Specifying an empty set is an error.
            + `ADD` - If the attribute does not already exist, then the attribute
                  and its values are added to the item. If the attribute does exist,
                  then the behavior of `ADD` depends on the data type of the
                  attribute:

                + If the existing attribute is a number, and if Value is also a number,
                      then the Value is mathematically added to the existing attribute.
                      If Value is a negative number, then it is subtracted from the
                      existing attribute. If you use `ADD` to increment or decrement a
                      number value for an item that doesn't exist before the update,
                      DynamoDB uses 0 as the initial value. In addition, if you use `ADD`
                      to update an existing item, and intend to increment or decrement an
                      attribute value which does not yet exist, DynamoDB uses `0` as the
                      initial value. For example, suppose that the item you want to
                      update does not yet have an attribute named itemcount , but you
                      decide to `ADD` the number `3` to this attribute anyway, even
                      though it currently does not exist. DynamoDB will create the
                      itemcount attribute, set its initial value to `0`, and finally add
                      `3` to it. The result will be a new itemcount attribute in the
                      item, with a value of `3`.
                + If the existing data type is a set, and if the Value is also a set,
                      then the Value is added to the existing set. (This is a set
                      operation, not mathematical addition.) For example, if the
                      attribute value was the set `[1,2]`, and the `ADD` action specified
                      `[3]`, then the final attribute value would be `[1,2,3]`. An error
                      occurs if an Add action is specified for a set attribute and the
                      attribute type specified does not match the existing set type. Both
                      sets must have the same primitive data type. For example, if the
                      existing data type is a set of strings, the Value must also be a
                      set of strings. The same holds true for number sets and binary
                      sets.
              This action is only valid for an existing attribute whose data type is
                  number or is a set. Do not use `ADD` for any other data types.
          **If no item with the specified Key is found:**

            + `PUT` - DynamoDB creates a new item with the specified primary key,
                  and then adds the attribute.
            + `DELETE` - Nothing happens; there is no attribute to delete.
            + `ADD` - DynamoDB creates an item with the supplied primary key and
                  number (or set of numbers) for the attribute value. The only data
                  types allowed are number and number set; no other data types can be
                  specified.



        If you specify any attributes that are part of an index key, then the
            data types for those attributes must match those of the schema in
            the table's attribute definition.

        :type expected: map
        :param expected:
        A map of attribute/condition pairs. This is the conditional block for
            the UpdateItem operation.

        Each element of Expected consists of an attribute name, a comparison
            operator, and one or more values. DynamoDB compares the attribute
            with the value(s) you supplied, using the comparison operator. For
            each Expected element, the result of the evaluation is either true
            or false.

        If you specify more than one element in the Expected map, then by
            default all of the conditions must evaluate to true. In other
            words, the conditions are ANDed together. (You can use the
            ConditionalOperator parameter to OR the conditions instead. If you
            do this, then at least one of the conditions must evaluate to true,
            rather than all of them.)

        If the Expected map evaluates to true, then the conditional operation
            succeeds; otherwise, it fails.

        Each item in Expected represents an attribute name for DynamoDB to
            check, along with an AttributeValueList and a ComparisonOperator :


        + AttributeValueList - One or more values to evaluate against the
              supplied attribute. The number of values in the list depends on the
              ComparisonOperator being used. For type Number, value comparisons
              are numeric. String value comparisons for greater than, equals, or
              less than are based on ASCII character code values. For example,
              `a` is greater than `A`, and `aa` is greater than `B`. For a list
              of code values, see
              `http://en.wikipedia.org/wiki/ASCII#ASCII_printable_characters`_.
              For Binary, DynamoDB treats each byte of the binary data as
              unsigned when it compares binary values, for example when
              evaluating query expressions.
        + ComparisonOperator - A comparator for evaluating attributes in the
              AttributeValueList . When performing the comparison, DynamoDB uses
              strongly consistent reads. The following comparison operators are
              available: `EQ | NE | LE | LT | GE | GT | NOT_NULL | NULL |
              CONTAINS | NOT_CONTAINS | BEGINS_WITH | IN | BETWEEN` The following
              are descriptions of each comparison operator.

            + `EQ` : Equal. AttributeValueList can contain only one AttributeValue
                of type String, Number, Binary, String Set, Number Set, or Binary
                Set. If an item contains an AttributeValue of a different type than
                the one specified in the request, the value does not match. For
                example, `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}`
                does not equal `{"NS":["6", "2", "1"]}`. > <li>
            + `NE` : Not equal. AttributeValueList can contain only one
                AttributeValue of type String, Number, Binary, String Set, Number
                Set, or Binary Set. If an item contains an AttributeValue of a
                different type than the one specified in the request, the value
                does not match. For example, `{"S":"6"}` does not equal
                `{"N":"6"}`. Also, `{"N":"6"}` does not equal `{"NS":["6", "2",
                "1"]}`. > <li>
            + `LE` : Less than or equal. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `LT` : Less than. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `GE` : Greater than or equal. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `GT` : Greater than. AttributeValueList can contain only one
                AttributeValue of type String, Number, or Binary (not a set). If an
                item contains an AttributeValue of a different type than the one
                specified in the request, the value does not match. For example,
                `{"S":"6"}` does not equal `{"N":"6"}`. Also, `{"N":"6"}` does not
                compare to `{"NS":["6", "2", "1"]}`. > <li>
            + `NOT_NULL` : The attribute exists.
            + `NULL` : The attribute does not exist.
            + `CONTAINS` : checks for a subsequence, or value in a set.
                  AttributeValueList can contain only one AttributeValue of type
                  String, Number, or Binary (not a set). If the target attribute of
                  the comparison is a String, then the operation checks for a
                  substring match. If the target attribute of the comparison is
                  Binary, then the operation looks for a subsequence of the target
                  that matches the input. If the target attribute of the comparison
                  is a set ("SS", "NS", or "BS"), then the operation checks for a
                  member of the set (not as a substring).
            + `NOT_CONTAINS` : checks for absence of a subsequence, or absence of a
                  value in a set. AttributeValueList can contain only one
                  AttributeValue of type String, Number, or Binary (not a set). If
                  the target attribute of the comparison is a String, then the
                  operation checks for the absence of a substring match. If the
                  target attribute of the comparison is Binary, then the operation
                  checks for the absence of a subsequence of the target that matches
                  the input. If the target attribute of the comparison is a set
                  ("SS", "NS", or "BS"), then the operation checks for the absence of
                  a member of the set (not as a substring).
            + `BEGINS_WITH` : checks for a prefix. AttributeValueList can contain
                only one AttributeValue of type String or Binary (not a Number or a
                set). The target attribute of the comparison must be a String or
                Binary (not a Number or a set). > <li>
            + `IN` : checks for exact matches. AttributeValueList can contain more
                  than one AttributeValue of type String, Number, or Binary (not a
                  set). The target attribute of the comparison must be of the same
                  type and exact value to match. A String never matches a String set.
            + `BETWEEN` : Greater than or equal to the first value, and less than
                  or equal to the second value. AttributeValueList must contain two
                  AttributeValue elements of the same type, either String, Number, or
                  Binary (not a set). A target attribute matches if the target value
                  is greater than, or equal to, the first element and less than, or
                  equal to, the second element. If an item contains an AttributeValue
                  of a different type than the one specified in the request, the
                  value does not match. For example, `{"S":"6"}` does not compare to
                  `{"N":"6"}`. Also, `{"N":"6"}` does not compare to `{"NS":["6",
                  "2", "1"]}`



        For usage examples of AttributeValueList and ComparisonOperator , see
            `Conditional Expressions`_ in the Amazon DynamoDB Developer Guide.


        For backward compatibility with previous DynamoDB releases, the
            following parameters can be used instead of AttributeValueList and
            ComparisonOperator :


        + Value - A value for DynamoDB to compare with an attribute.
        + Exists - Causes DynamoDB to evaluate the value before attempting the
              conditional operation:

            + If Exists is `True`, DynamoDB will check to see if that attribute
                  value already exists in the table. If it is found, then the
                  condition evaluates to true; otherwise the condition evaluate to
                  false.
            + If Exists is `False`, DynamoDB assumes that the attribute value does
                  not exist in the table. If in fact the value does not exist, then
                  the assumption is valid and the condition evaluates to true. If the
                  value is found, despite the assumption that it does not exist, the
                  condition evaluates to false.



        Even though DynamoDB continues to accept the Value and Exists
            parameters, they are now deprecated. We recommend that you use
            AttributeValueList and ComparisonOperator instead, since they allow
            you to construct a much wider range of conditions.

        The Value and Exists parameters are incompatible with
            AttributeValueList and ComparisonOperator . If you attempt to use
            both sets of parameters at once, DynamoDB will throw a
            ValidationException .

        :type conditional_operator: string
        :param conditional_operator: A logical operator to apply to the
            conditions in the Expected map:

        + `AND` - If all of the conditions evaluate to true, then the entire
              map evaluates to true.
        + `OR` - If at least one of the conditions evaluate to true, then the
              entire map evaluates to true.


        If you omit ConditionalOperator , then `AND` is the default.

        The operation will succeed only if the entire map evaluates to true.

        :type return_values: string
        :param return_values:
        Use ReturnValues if you want to get the item attributes as they
            appeared either before or after they were updated. For UpdateItem ,
            the valid values are:


        + `NONE` - If ReturnValues is not specified, or if its value is `NONE`,
              then nothing is returned. (This is the default for ReturnValues .)
        + `ALL_OLD` - If UpdateItem overwrote an attribute name-value pair,
              then the content of the old item is returned.
        + `UPDATED_OLD` - The old versions of only the updated attributes are
              returned.
        + `ALL_NEW` - All of the attributes of the new version of the item are
              returned.
        + `UPDATED_NEW` - The new versions of only the updated attributes are
              returned.

        :type return_consumed_capacity: string
        :param return_consumed_capacity: If set to `TOTAL`, the response
            includes ConsumedCapacity data for tables and indexes. If set to
            `INDEXES`, the response includes ConsumedCapacity for indexes. If
            set to `NONE` (the default), ConsumedCapacity is not included in
            the response.

        :type return_item_collection_metrics: string
        :param return_item_collection_metrics: If set to `SIZE`, statistics
            about item collections, if any, that were modified during the
            operation are returned in the response. If set to `NONE` (the
            default), no statistics are returned.

        """
        params = {'TableName': table_name, 'Key': key, }
        if attribute_updates is not None:
            params['AttributeUpdates'] = attribute_updates
        if expected is not None:
            params['Expected'] = expected
        if conditional_operator is not None:
            params['ConditionalOperator'] = conditional_operator
        if return_values is not None:
            params['ReturnValues'] = return_values
        if return_consumed_capacity is not None:
            params['ReturnConsumedCapacity'] = return_consumed_capacity
        if return_item_collection_metrics is not None:
            params['ReturnItemCollectionMetrics'] = return_item_collection_metrics
        return self.make_request(action='UpdateItem',
                                 body=json.dumps(params))

    def update_table(self, table_name, provisioned_throughput=None,
                     global_secondary_index_updates=None):
        """
        Updates the provisioned throughput for the given table.
        Setting the throughput for a table helps you manage
        performance and is part of the provisioned throughput feature
        of DynamoDB.

        The provisioned throughput values can be upgraded or
        downgraded based on the maximums and minimums listed in the
        `Limits`_ section in the Amazon DynamoDB Developer Guide.

        The table must be in the `ACTIVE` state for this operation to
        succeed. UpdateTable is an asynchronous operation; while
        executing the operation, the table is in the `UPDATING` state.
        While the table is in the `UPDATING` state, the table still
        has the provisioned throughput from before the call. The new
        provisioned throughput setting is in effect only when the
        table returns to the `ACTIVE` state after the UpdateTable
        operation.

        You cannot add, modify or delete indexes using UpdateTable .
        Indexes can only be defined at table creation time.

        :type table_name: string
        :param table_name: The name of the table to be updated.

        :type provisioned_throughput: dict
        :param provisioned_throughput: Represents the provisioned throughput
            settings for a specified table or index. The settings can be
            modified using the UpdateTable operation.
        For current minimum and maximum provisioned throughput values, see
            `Limits`_ in the Amazon DynamoDB Developer Guide.

        :type global_secondary_index_updates: list
        :param global_secondary_index_updates: An array of one or more global
            secondary indexes on the table, together with provisioned
            throughput settings for each index.

        """
        params = {'TableName': table_name, }
        if provisioned_throughput is not None:
            params['ProvisionedThroughput'] = provisioned_throughput
        if global_secondary_index_updates is not None:
            params['GlobalSecondaryIndexUpdates'] = global_secondary_index_updates
        return self.make_request(action='UpdateTable',
                                 body=json.dumps(params))

    def make_request(self, action, body):
        headers = {
            'X-Amz-Target': '%s.%s' % (self.TargetPrefix, action),
            'Host': self.host,
            'Content-Type': 'application/x-amz-json-1.0',
            'Content-Length': str(len(body)),
        }
        http_request = self.build_base_http_request(
            method='POST', path='/', auth_path='/', params={},
            headers=headers, data=body, host=self.host)
        response = self._mexe(http_request, sender=None,
                              override_num_retries=self.NumberRetries,
                              retry_handler=self._retry_handler)
        response_body = response.read()
        boto.log.debug(response_body)
        if response.status == 200:
            if response_body:
                return json.loads(response_body)
        else:
            json_body = json.loads(response_body)
            fault_name = json_body.get('__type', None)
            exception_class = self._faults.get(fault_name, self.ResponseError)
            raise exception_class(response.status, response.reason,
                                  body=json_body)

    def _retry_handler(self, response, i, next_sleep):
        status = None
        boto.log.debug("Saw HTTP status: %s" % response.status)
        if response.status == 400:
            response_body = response.read()
            boto.log.debug(response_body)
            data = json.loads(response_body)
            if 'ProvisionedThroughputExceededException' in data.get('__type'):
                self.throughput_exceeded_events += 1
                msg = "%s, retry attempt %s" % (
                    'ProvisionedThroughputExceededException',
                    i
                )
                next_sleep = self._truncated_exponential_time(i)
                i += 1
                status = (msg, i, next_sleep)
                if i == self.NumberRetries:
                    # If this was our last retry attempt, raise
                    # a specific error saying that the throughput
                    # was exceeded.
                    raise exceptions.ProvisionedThroughputExceededException(
                        response.status, response.reason, data)
            elif 'ConditionalCheckFailedException' in data.get('__type'):
                raise exceptions.ConditionalCheckFailedException(
                    response.status, response.reason, data)
            elif 'ValidationException' in data.get('__type'):
                raise exceptions.ValidationException(
                    response.status, response.reason, data)
            else:
                raise self.ResponseError(response.status, response.reason,
                                         data)
        expected_crc32 = response.getheader('x-amz-crc32')
        if self._validate_checksums and expected_crc32 is not None:
            boto.log.debug('Validating crc32 checksum for body: %s',
                           response.read())
            actual_crc32 = crc32(response.read()) & 0xffffffff
            expected_crc32 = int(expected_crc32)
            if actual_crc32 != expected_crc32:
                msg = ("The calculated checksum %s did not match the expected "
                       "checksum %s" % (actual_crc32, expected_crc32))
                status = (msg, i + 1, self._truncated_exponential_time(i))
        return status

    def _truncated_exponential_time(self, i):
        if i == 0:
            next_sleep = 0
        else:
            next_sleep = min(0.05 * (2 ** i),
                             boto.config.get('Boto', 'max_retry_delay', 60))
        return next_sleep
