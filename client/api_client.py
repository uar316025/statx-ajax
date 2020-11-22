"""API Client"""

import json
from datetime import datetime

import requests


class ApiException(Exception):
    """General API Exception"""


class StatxAPIv1:
    """Statx API v1 Client

    Args:
        address: API Address
    """

    def __init__(self, address):
        self.address = address
        self.session = requests.Session()

    def stat(self, operator: str = None):
        """Query statistics

        Args:
            operator: Filter by operator

        Returns:
            list[dict]: List of items

        Example::

            >>> api.stat()
            [
                {
                    'dev_tye': "Awesome device",
                    'count': 1337,
                    'successful': 1336,
                    'failed': 1
                },
                ...
            ]
        """
        try:
            resp = self.session.get(f'{self.address}/stat', params={'operator': operator})
        except Exception as exc:
            raise ApiException(str(exc)) from exc

        return _check_error(resp).json()

    def test_result_add(self, dev_type: str, operator: str, dt: datetime, success: bool) -> dict:
        """Add Test Result to Database

        Args:
            dev_type: Device type
            operator: Operators name
            dt: Test date
            success: Is passed successfully

        Returns:
            dict: Object with ID

        Example::

            >>> api.test_result_add(
            ...    'Awesome device','Awesome tester', datetime(2020,2,20), True
            ... )
            {'id': 1337 }
        """
        data = {
            'operator': operator,
            'dev_type': dev_type,
            'dt': dt.isoformat(),
            'success': int(success)
        }
        try:
            resp = self.session.post(f'{self.address}/test_result', data=data)
        except Exception as exc:
            raise ApiException(str(exc)) from exc

        return _check_error(resp).json()

    def test_result_delete(self, tests_id) -> bool:
        """Remove Test Result from Database

        Args:
            tests_id: ID of Test Result

        Returns:
            int: Number of removed rows

        Example::

            >>> api.test_result_delete(1337)
            1

        """
        try:
            resp = self.session.delete(f'{self.address}/test_result/{tests_id}')
        except Exception as exc:
            raise ApiException(str(exc)) from exc

        return _check_error(resp).json()


def _check_error(resp: requests.Response) -> requests.Response:
    """Wrapper to process error"""
    if resp.status_code != 200:
        try:
            # try decode API error message
            message = resp.json().get('message')
            raise ApiException(message)
        except json.JSONDecodeError:
            pass

        # is server exception
        raise ApiException(f'Server returns:\n{resp.text}\n[status {resp.status_code}]')
    return resp
