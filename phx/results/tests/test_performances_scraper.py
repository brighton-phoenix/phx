import datetime
from pathlib import Path

import responses
from athletes.models import Athlete
from django.test import TestCase
from faker import Faker
from results.models import Event, Performance, Result
from results.performances_scraper import PerformancesScraper

fake = Faker()


class TestPerformancesScraper(TestCase):

    @responses.activate
    def test_only_finds_performances_after_since_date(self):
        athlete = Athlete(power_of_10_id='1234',
                          created_date=datetime.datetime(2024, 1, 1))

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [
                {
                    "date": "1 May 24",
                    "meeting_id": 1234
                },
                {
                    "date": "1 Apr 24",
                    "meeting_id": 5678
                },
            ]
        }])

        scraper = PerformancesScraper()

        count = scraper.find_performances(athlete, datetime.date(2024, 5, 1))

        self.assertEqual(1, count)
        self.assertEqual(1, len(scraper.events))
        self.assertEqual(1, len(scraper.performances))

    @responses.activate
    def test_only_finds_performances_after_athlete_created_date(self):
        athlete = Athlete(power_of_10_id='1234',
                          created_date=datetime.datetime(2024, 5, 1))

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [
                {
                    "date": "1 May 24",
                    "meeting_id": 1234
                },
                {
                    "date": "1 Apr 24",
                    "meeting_id": 5678
                },
            ]
        }])

        scraper = PerformancesScraper()

        count = scraper.find_performances(athlete, datetime.date(2024, 1, 1))

        self.assertEqual(1, count)
        self.assertEqual(1, len(scraper.events))
        self.assertEqual(1, len(scraper.performances))

    @responses.activate
    def test_extracts_power_of_10_meeting_id_from_link(self):
        athlete = Athlete(power_of_10_id='1234',
                          created_date=datetime.datetime(2024, 5, 1))

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "1 May 24",
                "meeting_id": 5678
            }]
        }])

        scraper = PerformancesScraper()

        scraper.find_performances(athlete, datetime.date(2024, 1, 1))

        self.assertEqual('5678', scraper.events['5678'].power_of_10_meeting_id)

    @responses.activate
    def test_extracts_time_as_timedelta(self):
        athlete = Athlete(power_of_10_id='1234',
                          created_date=datetime.datetime(2024, 5, 1))

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "1 May 24",
                "meeting_id": '5555',
                "time": "1:20:30.40"
            }, {
                "date": "1 May 24",
                "meeting_id": '6666',
                "time": "20:30.40"
            }, {
                "date": "1 May 24",
                "meeting_id": '7777',
                "time": "30.40"
            }]
        }])

        scraper = PerformancesScraper()

        scraper.find_performances(athlete, datetime.date(2024, 1, 1))

        perf_1 = scraper.performances[0]
        perf_2 = scraper.performances[1]
        perf_3 = scraper.performances[2]

        self.assertEqual(
            perf_1.time,
            datetime.timedelta(hours=1,
                               minutes=20,
                               seconds=30,
                               milliseconds=400))
        self.assertEqual(
            perf_2.time,
            datetime.timedelta(minutes=20, seconds=30, milliseconds=400))

        self.assertEqual(
            perf_3.time,
            datetime.timedelta(seconds=30, milliseconds=400),
        )

    @responses.activate
    def test_considers_athelete_with_no_recent_performances_inactive(self):
        athlete = Athlete(power_of_10_id='1234',
                          created_date=datetime.datetime(2024, 5, 1))

        self.setup_profile_page([{
            "year":
            2022,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "1 May 22",
                "meeting_id": 5678
            }]
        }])

        scraper = PerformancesScraper()

        count = scraper.find_performances(athlete, datetime.date(2024, 1, 1))

        self.assertEqual(0, count)
        self.assertListEqual(['1234'], list(scraper.inactive_athletes))

    @responses.activate
    def test_considers_athletes_that_now_compete_for_another_club_inactive(
            self):
        athlete = Athlete(power_of_10_id='1234',
                          created_date=datetime.datetime(2024, 5, 1))

        self.setup_profile_page(
            [{
                "year": 2024,
                "club": "Another Club AC",
                "performances": [{
                    "date": "1 May 24",
                    "meeting_id": 5678
                }]
            }], "Another Club AC")

        scraper = PerformancesScraper()

        count = scraper.find_performances(athlete, datetime.date(2024, 1, 1))

        self.assertEqual(0, count)
        self.assertListEqual(['1234'], list(scraper.inactive_athletes))

    @responses.activate
    def test_doesnt_consider_new_athletes_with_no_performances_inactive(self):
        athlete = Athlete(power_of_10_id='1234',
                          created_date=datetime.datetime(2024, 5, 1))

        self.setup_profile_page(
            [{
                "year": 2024,
                "club": "Another Club AC",
                "performances": [{
                    "date": "1 May 24",
                    "meeting_id": 5678
                }]
            }], "Brighton Phoenix")

        scraper = PerformancesScraper()

        count = scraper.find_performances(athlete, datetime.date(2024, 1, 1))

        self.assertEqual(1, count)
        self.assertListEqual([], list(scraper.inactive_athletes))

    @responses.activate
    def test_can_scrape_multiple_performances_at_same_event(self):
        scraper = PerformancesScraper()

        athlete_one = Athlete(power_of_10_id='1234',
                              created_date=datetime.datetime(2024, 5, 1))

        # First athlete competed in heat and final
        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "1 May 24",
                "meeting_id": 9999,
                "round": "h1"
            }, {
                "date": "2 May 24",
                "meeting_id": 9999,
                "round": "f"
            }]
        }])

        count = scraper.find_performances(athlete_one,
                                          datetime.date(2024, 1, 1))

        self.assertEqual(2, count)
        self.assertEqual(1, len(scraper.events))
        self.assertEqual(2, len(scraper.performances))

        athlete_two = Athlete(power_of_10_id='5678',
                              created_date=datetime.datetime(2024, 5, 1))

        # Second athlete only competed in heat
        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "1 May 24",
                "meeting_id": 9999,
                "round": "h1"
            }]
        }])

        count = scraper.find_performances(athlete_two,
                                          datetime.date(2024, 1, 1))

        self.assertEqual(1, count)
        self.assertEqual(1, len(scraper.events))
        self.assertEqual(3, len(scraper.performances))

    @responses.activate
    def test_ignores_parkruns(self):
        athlete = Athlete(power_of_10_id='1234',
                          created_date=datetime.datetime(2024, 1, 1))

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [
                {
                    "date": "1 May 24",
                    "meeting_id": '5555',
                    "distance": "parkrun"
                },
                {
                    "date": "1 Apr 24",
                    "meeting_id": '6666',
                    "distance": "5K"
                },
            ]
        }])

        scraper = PerformancesScraper(include_parkrun=False)

        count = scraper.find_performances(athlete, datetime.date(2024, 4, 1))

        self.assertEqual(1, count)
        self.assertEqual(1, len(scraper.events))
        self.assertEqual(1, len(scraper.performances))

    @responses.activate
    def test_save_stores_new_performances_in_database(self):
        athlete = Athlete(power_of_10_id='1234')

        athlete.save()
        athlete.created_date = datetime.datetime(2024, 1, 1)

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "1 May 24",
                "meeting_id": '5678'
            }]
        }])

        scraper = PerformancesScraper()
        scraper.find_performances(athlete, datetime.date(2024, 1, 1))
        scraper.save()

        self.assertEqual(1, len(Performance.objects.all()))
        self.assertEqual(1, len(Event.objects.all()))

    @responses.activate
    def test_save_updates_athlete_last_checked_field(self):
        athlete = Athlete(power_of_10_id='1234')
        athlete.save()

        self.setup_profile_page([{
            "year": 2024,
            "club": "Brighton Phoenix",
            "performances": []
        }])

        scraper = PerformancesScraper()
        scraper.find_performances(athlete, datetime.date(2024, 1, 1))
        scraper.save()

        athlete.refresh_from_db()

        self.assertTrue(athlete.last_checked)

    @responses.activate
    def test_save_updates_existing_performances_in_database(self):
        athlete = Athlete(power_of_10_id='1234')

        athlete.save()
        athlete.created_date = datetime.datetime(2024, 1, 1)

        event = Event(name='parkrun',
                      location='Preston Park',
                      power_of_10_meeting_id='5678')
        event.save()

        performance = Performance(athlete=athlete,
                                  event=event,
                                  date=datetime.date(2024, 5, 1),
                                  category='MV35',
                                  distance='parkrun',
                                  overall_position=1,
                                  round='',
                                  time=datetime.timedelta(minutes=20))

        performance.save()

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "1 May 24",
                "meeting_id": '5678',
                "distance": "parkrun",
                "round": ''
            }]
        }])

        scraper = PerformancesScraper()
        scraper.find_performances(athlete, datetime.date(2024, 1, 1))
        scraper.save()

        self.assertEqual(1, len(Performance.objects.all()))
        self.assertEqual(1, len(Event.objects.all()))

    @responses.activate
    def test_save_updates_the_status_of_inactive_athletes(self):
        athlete = Athlete(power_of_10_id='1234')

        athlete.save()
        athlete.created_date = datetime.datetime(2024, 5, 1)

        self.setup_profile_page([{
            "year":
            2022,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "1 May 22",
                "meeting_id": 5678
            }]
        }])

        scraper = PerformancesScraper()

        scraper.find_performances(athlete, datetime.date(2024, 1, 1))
        scraper.save()

        self.assertFalse(Athlete.objects.all()[0].active)

    @responses.activate
    def test_save_creates_draft_result_for_each_event(self):
        athlete = Athlete(power_of_10_id='1234')

        athlete.save()
        athlete.created_date = datetime.datetime(2024, 1, 1)

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "1 May 24",
                "meeting_id": '5678',
                "distance": "5K",
                "meeting": "Brighton 5K"
            }, {
                "date": "2 May 24",
                "meeting_id": '9999',
                "distance": "parkrun",
                "meeting": "Preston Park parkrun"
            }]
        }])

        scraper = PerformancesScraper()
        scraper.find_performances(athlete, datetime.date(2024, 1, 1))
        scraper.save()

        events = Event.objects.all()
        results = Result.objects.all()

        self.assertEqual(2, len(events))
        self.assertEqual(2, len(results))
        self.assertEqual(events[0].result, results[0])

        self.assertTrue(results[0].draft)
        self.assertEqual(events[0].date, results[0].event_date)
        self.assertTrue(events[0].name in results[0].title)

        self.assertTrue(results[1].draft)
        self.assertEqual(events[1].date, results[1].event_date)
        self.assertEqual("parkrun - week 18", results[1].title)

    @responses.activate
    def test_save_doesnt_create_new_result_if_already_exists(self):
        athlete = Athlete(power_of_10_id='1234')

        athlete.save()
        athlete.created_date = datetime.datetime(2024, 1, 1)

        result = Result.objects.create(title="parkrun - Preston Park",
                                       event_date=datetime.datetime(
                                           2024, 5, 1))

        Event.objects.create(name='parkrun',
                             location='Preston Park',
                             power_of_10_meeting_id='5678',
                             result=result)

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "1 May 24",
                "meeting_id": '5678'
            }]
        }])

        scraper = PerformancesScraper()
        scraper.find_performances(athlete, datetime.date(2024, 1, 1))
        scraper.save()

        events = Event.objects.all()
        results = Result.objects.all()

        self.assertEqual(1, len(events))
        self.assertEqual(1, len(results))
        self.assertEqual(events[0].result, results[0])

    @responses.activate
    def test_save_links_all_parkruns_in_same_week_to_same_result(self):
        athlete = Athlete(power_of_10_id='1234')

        athlete.save()
        athlete.created_date = datetime.datetime(2024, 1, 1)

        Result.objects.create(title="parkrun - week 32",
                              event_date=datetime.datetime(2024, 8, 10))

        Result.objects.create(title="parkrun - week 33",
                              event_date=datetime.datetime(2024, 8, 17))

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "10 Aug 24",
                "meeting_id": '1111',
                "distance": "parkrun"
            }, {
                "date": "17 Aug 24",
                "meeting_id": '2222',
                "distance": "parkrun"
            }, {
                "date": "24 Aug 24",
                "meeting_id": '3333',
                "distance": "parkrun"
            }]
        }])

        scraper = PerformancesScraper()
        scraper.find_performances(athlete, datetime.date(2024, 1, 1))
        scraper.save()

        events = Event.objects.all()
        results = Result.objects.all()

        self.assertEqual(3, len(events))
        self.assertEqual(3, len(results))
        self.assertEqual(events[0].result, results[0])
        self.assertEqual(events[1].result, results[1])
        self.assertEqual(events[2].result, results[2])

    @responses.activate
    def test_ignores_invalid_results(self):
        athlete = Athlete(power_of_10_id='1234',
                          created_date=datetime.datetime(2024, 1, 1))

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [
                {
                    "date": "1 May 24",
                    "meeting_id": "1111",
                    "position": "-",
                    "time": "DNF"
                },
                {
                    "date": "2 May 24",
                    "meeting_id": "2222",
                    "time": "NT"
                },
                {
                    "date": "3 May 24",
                    "meeting_id": "3333",
                    "time": "DQ"
                },
                {
                    "date": "1 Apr 24",
                    "meeting_id": "4444"
                },
            ]
        }])

        scraper = PerformancesScraper()

        count = scraper.find_performances(athlete, datetime.date(2024, 4, 1))

        self.assertEqual(1, count)
        self.assertEqual(1, len(scraper.events))
        self.assertEqual(1, len(scraper.performances))

    @responses.activate
    def test_can_parse_string_positions(self):
        athlete = Athlete(power_of_10_id='1234')

        athlete.save()
        athlete.created_date = datetime.datetime(2024, 1, 1)

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "1 May 24",
                "meeting_id": "1234",
                "position": "L3",
            }]
        }])

        scraper = PerformancesScraper()

        scraper.find_performances(athlete, datetime.date(2024, 5, 1))
        self.assertEqual((1, 1, 0), scraper.save())

    @responses.activate
    def test_ignore_invalid_performances_at_same_event(self):
        athlete = Athlete(power_of_10_id='1234')

        athlete.save()
        athlete.created_date = datetime.datetime(2024, 1, 1)

        self.setup_profile_page([{
            "year":
            2024,
            "club":
            "Brighton Phoenix",
            "performances": [{
                "date": "1 May 24",
                "meeting_id": "1234",
                "position": "9",
                "distance": "10K",
                "time": "36:35",
                "round": ""
            }, {
                "date": "1 May 24",
                "meeting_id": "1234",
                "position": "107",
                "distance": "10K",
                "time": "47:50",
                "round": ""
            }]
        }])

        scraper = PerformancesScraper()

        scraper.find_performances(athlete, datetime.date(2024, 5, 1))

        # There are two performances for the same athlete, event, distance
        # and round. One of them must be invalid so we arbitrarily ignore
        # the second.
        self.assertEqual((1, 1, 0), scraper.save())

    @responses.activate
    def test_dont_crash_when_profile_missing(self):
        athlete = Athlete(power_of_10_id='1234')

        athlete.save()
        scraper = PerformancesScraper()

        responses.get("https://www.thepowerof10.info/athletes/profile.aspx",
                      body="<html>Profile not found</html>",
                      content_type='text/plain',
                      status=200)

        scraper.find_performances(athlete, datetime.date(2024, 5, 1))

    def test_publishes_results_for_events_created_today(self):
        result = Result.objects.create(title="parkrun - Preston Park",
                                       event_date=datetime.datetime.now(),
                                       draft=True)

        Event.objects.create(name='parkrun',
                             location='Preston Park',
                             power_of_10_meeting_id='5678',
                             result=result)

        self.assertEqual(1, PerformancesScraper().publish_results())

        result.refresh_from_db()

        self.assertFalse(result.draft)

    def test_doesnt_publish_results_for_events_not_created_today(self):
        past = datetime.datetime(2024, 5, 1, tzinfo=datetime.timezone.utc)
        result = Result.objects.create(title="parkrun - Preston Park",
                                       event_date=past,
                                       draft=True)

        event = Event.objects.create(name='parkrun',
                                     location='Preston Park',
                                     power_of_10_meeting_id='5678',
                                     result=result)

        event.created_date = past
        event.save()

        self.assertEqual(0, PerformancesScraper().publish_results())

        result.refresh_from_db()

        self.assertTrue(result.draft)

    def setup_profile_page(self,
                           performances,
                           current_club="Brighton Phoenix"):
        rows = []
        for group in performances:
            year = group['year']
            club = group['club']

            rows.append(f"""
                <tr style="background-color:DarkGray;">
                    <td colspan="12">
                        <a name="{year}"><b>{year} V35 {club}</b>
                    </td>
                </tr>
                """)

            rows.append("""
                <tr style="background-color:LightGrey;">
                    <td><b>Event</b></td>
                    <td><b>Perf</b></td>
                    <td></td><td></td>
                    <td></td>
                    <td><b>Pos</b></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td><b>Venue</b></td>
                    <td><b>Meeting</b></td>
                    <td align="right"><b>Date</b></td>
                </tr>
                """)

            for performance in group['performances']:
                meeting = performance.get("meeting", "Preston Park parkrun")
                meeting_date = performance.get("date", "1 Aug 24")
                meeting_id = performance.get("meeting_id", 1234)

                rows.append(f"""
                    <tr style="background-color:Gainsboro;">
                        <td>{performance.get("distance", "parkrun")}</td>
                        <td>{performance.get("time", "20:00")}</td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td>{performance.get("position", 1)}</td>
                        <td>{performance.get("round", "")}</td>
                        <td></td>
                        <td></td>
                        <td>
                            <a href="results.aspx?meetingid={meeting_id}">
                                {performance.get("location", "Preston Park")}
                            </a>
                        </td>
                        <td>{meeting}</td>
                        <td align="right">{meeting_date}</td>
                    </tr>
                    """)
        text = Path(__file__).with_name('test_body.html').read_text()

        body = text.replace("{rows}", ''.join(rows)) \
                   .replace("{current_club}", current_club)

        responses.get("https://www.thepowerof10.info/athletes/profile.aspx",
                      body=body,
                      content_type='text/plain',
                      status=200)
