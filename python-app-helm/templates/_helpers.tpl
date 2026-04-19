{{/*
Expand the name of the chart.
*/}}
{{- define "python-app.name" -}}
{{- default .Chart.Name .Values.global.appName | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a full name for resources.
*/}}
{{- define "python-app.fullname" -}}
{{- if .Values.global.fullnameOverride }}
{{- .Values.global.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.global.appName -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Common labels for resources.
*/}}
{{- define "python-app.labels" -}}
helm.sh/chart: {{ include "python-app.chart" . }}
app.kubernetes.io/name: {{ include "python-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
environment: {{ .Values.global.environment }}
{{- end -}}

{{/*
Chart label helper.
*/}}
{{- define "python-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Service labels helper.
*/}}
{{- define "python-app.serviceLabels" -}}
app: {{ index .Values.services .service "name" }}
environment: {{ .Values.global.environment }}
{{- end -}}

{{/*
Service selector labels helper.
*/}}
{{- define "python-app.serviceSelectorLabels" -}}
app: {{ index .Values.services .service "name" }}
environment: {{ .Values.global.environment }}
{{- end -}}

{{/*
Image helper for a specific service.
*/}}
{{- define "python-app.image" -}}
{{- $svc := .service -}}
{{- $image := index .Values.services $svc "image" -}}
{{- printf "%s:%s" $image.repository $image.tag -}}
{{- end -}}
