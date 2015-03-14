# About

This is the repository for the [Publish/Subscriber Server exercise](./exercise.md).

## How to prepare the environment

*  Checkout the code
*  Create and activate new `virtualenv`
*  `$ pip install -r ./requirements.txt`

## How to run tests
*  Activate the above `virtualenv`

```
$ ./bin/test.sh
tests.subscriber_server.test_db
  TestDataStorage
    test_database_op_cycle ...                                             [OK]
    test_interface ...                                                     [OK]
    test_many_messages_many_users ...                                      [OK]
    test_persistence ...                                                   [OK]
tests.subscriber_server.test_resource
  TestWebResource
    test_get_no_messages_in_queue ...                                      [OK]
    test_get_not_subscribed ...                                            [OK]
    test_get_ok ...                                                        [OK]
    test_publish ...                                                       [OK]
    test_subscribe ...                                                     [OK]
    test_unsubscribe_not_subscribed ...                                    [OK]
    test_unsubscribe_ok ...                                                [OK]

-------------------------------------------------------------------------------
Ran 11 tests in 0.286s

PASSED (successes=11)
```

## How to deploy
*  Activate the `virtualenv`

```
  $ ./bin/serve.sh
  Starting the Publish/Subscribe server at the port 5000 (using database './publish_subscribe.db')
```

### How to interact with

To interact with the server, I've added a simple prtogram called `client` to the `bin` directory.
It is effectively a CLI client for the server.

The program executes a single API call per its invocation and prints out a response from server (json-encoded).

Example of usage:
```
$ ./bin/client subscribe kittens_and_puppies Alice
{
  "content": "Subscription succeeded.",
  "status_code": 200
}
$ ./bin/client subscribe kittens_and_puppies Bob
{
  "content": "Subscription succeeded.",
  "status_code": 200
}
$ ./bin/client publish kittens_and_puppies XXX_UNUSED --payload "http://cuteoverload.files.wordpress.com/2014/10/unnamed23.jpg?w=750&h=1000"
{
  "content": "Publish succeeded.",
  "status_code": 200
}
$ ./bin/client get kittens_and_puppies Alice
{
  "content": "http://cuteoverload.files.wordpress.com/2014/10/unnamed23.jpg?w=750&h=1000",
  "status_code": 200
}
$ ./bin/client get kittens_and_puppies Alice
{
  "content": "",
  "status_code": 204
}
$ ./bin/client get kittens_and_puppies Eve
{
  "content": "The subscription does not exist.",
  "status_code": 404
}
$ ./bin/client get kittens_and_puppies Bob
{
  "content": "http://cuteoverload.files.wordpress.com/2014/10/unnamed23.jpg?w=750&h=1000",
  "status_code": 200
}
$ ./bin/client get kittens_and_puppies Bob
{
  "content": "",
  "status_code": 204
}
```

### How did I ensure the product quality of the code

1.  Unittests (`$ ./bin/test.sh`)
1.  PyLint (`$ ./bin/pylint.sh`)
1.  Manual integration tests with the `client` program

### What I left out
1. Automated integration tests
1. Stress tests
1. Better `pylint` score
1. Improve performance (db access is pretty much exclusive, and its performance is rather unsatisfactory)
1. More meaningful leverage of `zope.interface` via component registration


### P.S.

Messages are actually persistent and won't disappear with server restart.
