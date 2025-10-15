
from django.test import TestCase
from rest_framework.test import APITestCase
from .serializers import InmobiliariaSerializer, UbicacionInmobiliariaSerializer, RedesSocialesSerializer
from .models import Inmobiliaria, UbicacionInmobiliaria
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

class InmobiliariaSerializerTest(APITestCase):
	def test_valid_data(self):
		data = {
			"nombre": "Test Inmobiliaria",
			"telefono": "123456789",
			"celular": "+51987654321",
			"email": "test@correo.com",
			"facebook": "https://facebook.com/test",
			"instagram": "https://instagram.com/test",
			"twitter": "https://twitter.com/test",
			"youtube": "https://youtube.com/test"
		}
		serializer = InmobiliariaSerializer(data=data)
		self.assertTrue(serializer.is_valid())

	def test_invalid_email(self):
		data = {
			"nombre": "Test Inmobiliaria",
			"email": "no-es-email"
		}
		serializer = InmobiliariaSerializer(data=data)
		self.assertFalse(serializer.is_valid())

class UbicacionInmobiliariaSerializerTest(APITestCase):
	def setUp(self):
		self.inmobiliaria = Inmobiliaria.objects.create(nombre="Test", email="test@correo.com")

	def test_valid_data(self):
		data = {
			"id_inmobiliaria": self.inmobiliaria.id,
			"direccion": "Av. Principal 123",
			"departamento": "Lima",
			"ciudad": "Lima",
			"distrito": "Miraflores",
			"latitud": -12.123456,
			"longitud": -77.123456
		}
		serializer = UbicacionInmobiliariaSerializer(data=data)
		self.assertTrue(serializer.is_valid())

	def test_missing_inmobiliaria(self):
		data = {
			"direccion": "Av. Principal 123"
		}
		serializer = UbicacionInmobiliariaSerializer(data=data)
		self.assertFalse(serializer.is_valid())

class RedesSocialesSerializerTest(APITestCase):
	def test_valid_urls(self):
		data = {
			"facebook": "https://facebook.com/test",
			"twitter": "https://twitter.com/test",
			"instagram": "https://instagram.com/test",
			"youtube": "https://youtube.com/test"
		}
		serializer = RedesSocialesSerializer(data=data)
		self.assertTrue(serializer.is_valid())

	def test_invalid_url(self):
		data = {
			"facebook": "no-es-url"
		}
		serializer = RedesSocialesSerializer(data=data)
		self.assertFalse(serializer.is_valid())


class InmobiliariaViewSetTestCase(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(email="testuser@correo.com", password="testpass")
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)
		self.inmobiliaria = Inmobiliaria.objects.create(
			nombre="Test Inmobiliaria",
			email="test@correo.com"
		)

	def test_list_inmobiliarias(self):
		url = reverse('inmobiliaria-list')
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn("Test Inmobiliaria", response.content.decode())

	def test_create_inmobiliaria(self):
		url = reverse('inmobiliaria-list')
		data = {
			"nombre": "Nueva Inmobiliaria",
			"email": "nueva@correo.com"
		}
		response = self.client.post(url, data)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["nombre"], "Nueva Inmobiliaria")

	def test_update_inmobiliaria(self):
		url = reverse('inmobiliaria-detail', args=[self.inmobiliaria.id])
		data = {"nombre": "Actualizada", "email": "actualizada@correo.com"}
		response = self.client.put(url, data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["nombre"], "Actualizada")

	def test_delete_inmobiliaria(self):
		url = reverse('inmobiliaria-detail', args=[self.inmobiliaria.id])
		response = self.client.delete(url)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class UbicacionInmobiliariaViewSetTestCase(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(email="testuser2@correo.com", password="testpass")
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)
		self.inmobiliaria = Inmobiliaria.objects.create(nombre="Test", email="test@correo.com")
		self.ubicacion = UbicacionInmobiliaria.objects.create(
			id_inmobiliaria=self.inmobiliaria,
			direccion="Av. Principal 123",
			departamento="Lima",
			ciudad="Lima",
			distrito="Miraflores",
			latitud=-12.123456,
			longitud=-77.123456
		)

	def test_list_ubicaciones(self):
		url = reverse('ubicacioninmobiliaria-list')
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn("Av. Principal 123", response.content.decode())

	def test_create_ubicacion(self):
		url = reverse('ubicacioninmobiliaria-list')
		nueva_inmobiliaria = Inmobiliaria.objects.create(nombre="Otra Inmobiliaria", email="otra@correo.com")
		data = {
			"id_inmobiliaria": nueva_inmobiliaria.id,
			"direccion": "Av. Secundaria 456",
			"departamento": "Lima",
			"ciudad": "Lima",
			"distrito": "San Isidro",
			"latitud": -12.111111,
			"longitud": -77.111111
		}
		response = self.client.post(url, data)
		print("Ubicacion POST response:", response.data)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["direccion"], "Av. Secundaria 456")

	def test_update_ubicacion(self):
		url = reverse('ubicacioninmobiliaria-detail', args=[self.ubicacion.id])
		data = {
			"id_inmobiliaria": self.inmobiliaria.id,
			"direccion": "Av. Actualizada",
			"departamento": "Lima",
			"ciudad": "Lima",
			"distrito": "San Isidro",
			"latitud": -12.111111,
			"longitud": -77.111111
		}
		response = self.client.put(url, data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["direccion"], "Av. Actualizada")

	def test_delete_ubicacion(self):
		url = reverse('ubicacioninmobiliaria-detail', args=[self.ubicacion.id])
		response = self.client.delete(url)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)