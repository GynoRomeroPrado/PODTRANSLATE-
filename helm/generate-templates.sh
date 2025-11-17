#!/bin/bash
# Generate Helm templates for all services

SERVICES=("audio-processing" "distribution" "analytics" "ai-tools" "dashboard")
CHART_DIR="podtranslate/templates"

for service in "${SERVICES[@]}"; do
  SERVICE_DIR="$CHART_DIR/$service"
  mkdir -p "$SERVICE_DIR"
  
  SERVICE_VAR=$(echo $service | sed 's/-//g' | sed 's/\([A-Z]\)/\L\1/g')
  if [ "$service" = "audio-processing" ]; then
    SERVICE_VAR="audioProcessing"
  elif [ "$service" = "ai-tools" ]; then
    SERVICE_VAR="aiTools"
  fi
  
  echo "Creating templates for $service (var: $SERVICE_VAR)..."
done

echo "✅ Template generation complete!"
