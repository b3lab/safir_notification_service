#!/usr/bin/env bash


export TOKEN=`curl -i -H "Content-Type: application/json" -d '
{ "auth": {
      "identity": {
        "methods": ["password"],
        "password": {
          "user": {
            "name": "admin",
            "domain": { "name": "default" },
            "password": "1234qweR"
          }
        }
      },
      "scope": {
        "project": {
          "name": "admin",
          "domain": { "name": "default" }
        }
      }
   }
}' "http://172.16.1.43/identity/v3/auth/tokens" | awk '/X-Subject-Token/ {print $2}'`


test_info ()
{
    echo 'GET http://altyapitest.b3lab.org:9764/v1/info/currency'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/info/currency"
    echo ''
    echo 'GET http://altyapitest.b3lab.org:9764/v1/info/method'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/info/method"
    echo ''
    echo 'GET http://altyapitest.b3lab.org:9764/v1/info/suspension_limit'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/info/suspension_limit"
    echo ''
    echo 'GET http://altyapitest.b3lab.org:9764/v1/info/termination_limit'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/info/termination_limit"
    echo ''
    echo 'GET http://altyapitest.b3lab.org:9764/v1/info/notification_limit'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/info/notification_limit"
    echo ''
    echo 'GET http://altyapitest.b3lab.org:9764/v1/info/new_resource_limit'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/info/new_resource_limit"
    echo ''
}

test_customer ()
{
    echo 'GET http://altyapitest.b3lab.org:9764/v1/customer'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/customer/"
    echo ''
    echo 'GET http://altyapitest.b3lab.org:9764/v1/customer/1c3ea2c26caa4bdb9a3cdaa080d7af95'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/customer/1c3ea2c26caa4bdb9a3cdaa080d7af95"
    echo ''
    # curl -X PUT -i -H "Content-Type: application/json" -H "Accept: application/json"  -H "X-Auth-Token: $TOKEN"  "http://altyapitest.b3lab.org:9764/v1/customer/cf4a85294f554912a54cff1e7e9780c0" -d '{"project_id": "cf4a85294f554912a54cff1e7e9780c0", "description": "demo", "company_name": "B3LAB", "mail": "safir.iletisim@b3lab.org"}'
    echo ''
}

test_credit ()
{
    echo 'GET http://altyapitest.b3lab.org:9764/v1/credit'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/credit/"
    echo ''
    echo 'GET http://altyapitest.b3lab.org:9764/v1/credit/1c3ea2c26caa4bdb9a3cdaa080d7af95'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/credit/1c3ea2c26caa4bdb9a3cdaa080d7af95"
    echo ''
    echo 'GET http://altyapitest.b3lab.org:9764/v1/credit/activities?project_id=1c3ea2c26caa4bdb9a3cdaa080d7af95'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/credit/activities?project_id=1c3ea2c26caa4bdb9a3cdaa080d7af95"
    echo ''
    # curl -X PUT -i -H "Content-Type: application/json" -H "Accept: application/json"  -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/credit/cf4a85294f554912a54cff1e7e9780c0" -d '{"credit":"1000"}'
    echo ''
    # curl -X PUT -i -H "Content-Type: application/json" -H "Accept: application/json"  -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/credit/load/cf4a85294f554912a54cff1e7e9780c0" -d '{"amount":"500"}'
    echo ''
}

test_invoice ()
{
    echo 'GET http://altyapitest.b3lab.org:9764/v1/invoice'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/invoice/"
    echo ''
    echo 'GET http://altyapitest.b3lab.org:9764/v1/invoice/1c3ea2c26caa4bdb9a3cdaa080d7af95/paid'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/invoice/1c3ea2c26caa4bdb9a3cdaa080d7af95/paid"
    echo ''
    # curl -X PUT -i -H "Content-Type: application/json" -H "Accept: application/json" -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/invoice/c491895f-c170-4493-bb57-1ba738f28206" -d '{"amount":"500", "currency":"TL", "issue_date":"2017-10-27T11:31:44", "due_date":"2017-10-30T11:31:44", "status":"unpaid"}'
    echo ''
}

test_report ()
{
    echo 'GET http://altyapitest.b3lab.org:9764/v1/report/1c3ea2c26caa4bdb9a3cdaa080d7af95'
    curl -H "X-Auth-Token: $TOKEN" "http://altyapitest.b3lab.org:9764/v1/report/1c3ea2c26caa4bdb9a3cdaa080d7af95/"
    echo ''
}

test_info
test_customer
test_credit
test_invoice