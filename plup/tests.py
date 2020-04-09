# from django.urls import reverse
# from rest_framework.test import APITestCase, APIClient
# from rest_framework.views import status
# from .models import scenario
# from .serializers import scenarioSerializer

# # tests for views


# class BaseViewTest(APITestCase):
#     client = APIClient()

#     @staticmethod
#     def create_scenario(title="", artist=""):
#         if title != "" and artist != "":
#             scenario.objects.create(scenario_id, name,description, owner_id)

#     # def setUp(self):
#     #     # add test data
#     #     self.create_scenario("like glue", "sean paul")
#     #     self.create_scenario("simple scenario", "konshens")
#     #     self.create_scenario("love is wicked", "brick and lace")
#     #     self.create_scenario("jam rock", "damien marley")


# class GetAllscenariosTest(BaseViewTest):

#     def test_get_all_scenarios(self):
#         """
#         This test ensures that all scenarios added in the setUp method
#         exist when we make a GET request to the scenarios/ endpoint
#         """
#         # hit the API endpoint
#         response = self.client.get(
#             reverse("scenarios-all", kwargs={"version": "v1"})
#         )
#         # fetch the data from db
#         expected = scenario.objects.all()
#         serialized = scenarioSerializer(expected, many=True)
#         self.assertEqual(response.data, serialized.data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)