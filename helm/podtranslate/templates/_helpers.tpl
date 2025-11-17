{{/*
Expand the name of the chart.
*/}}
{{- define "podtranslate.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "podtranslate.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "podtranslate.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "podtranslate.labels" -}}
helm.sh/chart: {{ include "podtranslate.chart" . }}
{{ include "podtranslate.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "podtranslate.selectorLabels" -}}
app.kubernetes.io/name: {{ include "podtranslate.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Component-specific labels
*/}}
{{- define "podtranslate.componentLabels" -}}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{/*
PostgreSQL host
*/}}
{{- define "podtranslate.postgresql.host" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" (include "podtranslate.fullname" .) }}
{{- else }}
{{- .Values.postgresql.external.host }}
{{- end }}
{{- end }}

{{/*
Redis host
*/}}
{{- define "podtranslate.redis.host" -}}
{{- if .Values.redis.enabled }}
{{- printf "%s-redis-master" (include "podtranslate.fullname" .) }}
{{- else }}
{{- .Values.redis.external.host }}
{{- end }}
{{- end }}

{{/*
RabbitMQ host
*/}}
{{- define "podtranslate.rabbitmq.host" -}}
{{- if .Values.rabbitmq.enabled }}
{{- printf "%s-rabbitmq" (include "podtranslate.fullname" .) }}
{{- else }}
{{- .Values.rabbitmq.external.host }}
{{- end }}
{{- end }}

{{/*
Database URL
*/}}
{{- define "podtranslate.database.url" -}}
postgresql://{{ .Values.postgresql.auth.username }}:{{ .Values.postgresql.auth.password }}@{{ include "podtranslate.postgresql.host" . }}:5432/{{ .Values.postgresql.auth.database }}
{{- end }}

{{/*
Redis URL
*/}}
{{- define "podtranslate.redis.url" -}}
redis://:{{ .Values.redis.auth.password }}@{{ include "podtranslate.redis.host" . }}:6379/0
{{- end }}

{{/*
RabbitMQ URL
*/}}
{{- define "podtranslate.rabbitmq.url" -}}
amqp://{{ .Values.rabbitmq.auth.username }}:{{ .Values.rabbitmq.auth.password }}@{{ include "podtranslate.rabbitmq.host" . }}:5672
{{- end }}
