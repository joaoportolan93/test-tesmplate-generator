$(document).ready(function() {
    // Carregar lista de testes
    loadTests();

    // Handlers para adicionar itens dinâmicos
    $('#addStepBtn').click(addStep);
    $('#addEnvBtn').click(addEnvironmentVar);
    $('#addCustomFieldBtn').click(addCustomField);

    // Handler para novo teste
    $('#newTestBtn').click(function() {
        $('#testForm')[0].reset();
        $('#stepsList').empty();
        $('#envList').empty();
        $('#customFieldsList').empty();
    });

    // Handler para submissão do formulário
    $('#testForm').submit(function(e) {
        e.preventDefault();
        saveTest();
    });
});

function loadTests() {
    $.get('/api/tests', function(tests) {
        $('#testList').empty();
        tests.forEach(function(test) {
            addTestToList(test);
        });
    });
}

function addTestToList(test) {
    const statusClass = `status-${test[3]}`;
    const item = $(`
        <a href="#" class="list-group-item list-group-item-action" data-id="${test[0]}">
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${test[1]}</h6>
                <span class="status-badge ${statusClass}">${test[3]}</span>
            </div>
            <p class="mb-1">${test[2] || ''}</p>
            <small class="timestamp">${test[4]}</small>
        </a>
    `);
    
    item.click(function() {
        loadTestDetails(test[0]);
    });
    
    $('#testList').append(item);
}

function addStep() {
    const stepHtml = `
        <div class="step-item">
            <i class="material-icons remove-btn">close</i>
            <div class="mb-3">
                <label class="form-label">Descrição do Step</label>
                <input type="text" class="form-control step-description" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Status</label>
                <select class="form-select step-status">
                    <option value="info">Info</option>
                    <option value="pass">Pass</option>
                    <option value="fail">Fail</option>
                    <option value="warning">Warning</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Detalhes</label>
                <textarea class="form-control step-details" rows="2"></textarea>
            </div>
        </div>
    `;
    $('#stepsList').append(stepHtml);
    
    // Handler para remover step
    $('.remove-btn').click(function() {
        $(this).closest('.step-item').remove();
    });
}

function addEnvironmentVar() {
    const envHtml = `
        <div class="env-item">
            <i class="material-icons remove-btn">close</i>
            <div class="row">
                <div class="col-md-5">
                    <input type="text" class="form-control env-key" placeholder="Nome da Variável" required>
                </div>
                <div class="col-md-7">
                    <input type="text" class="form-control env-value" placeholder="Valor" required>
                </div>
            </div>
        </div>
    `;
    $('#envList').append(envHtml);
    
    // Handler para remover variável
    $('.remove-btn').click(function() {
        $(this).closest('.env-item').remove();
    });
}

function addCustomField() {
    const fieldHtml = `
        <div class="custom-field-item">
            <i class="material-icons remove-btn">close</i>
            <div class="row">
                <div class="col-md-5">
                    <input type="text" class="form-control custom-field-name" placeholder="Nome do Campo" required>
                </div>
                <div class="col-md-7">
                    <input type="text" class="form-control custom-field-value" placeholder="Valor" required>
                </div>
            </div>
        </div>
    `;
    $('#customFieldsList').append(fieldHtml);
    
    // Handler para remover campo
    $('.remove-btn').click(function() {
        $(this).closest('.custom-field-item').remove();
    });
}

function saveTest() {
    const formData = {
        name: $('input[name="name"]').val(),
        description: $('textarea[name="description"]').val(),
        status: $('select[name="status"]').val(),
        categories: $('input[name="categories"]').val().split(',').map(c => c.trim()),
        steps: getSteps(),
        environment: getEnvironment(),
        custom_fields: getCustomFields()
    };

    $.ajax({
        url: '/api/tests',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.status === 'success') {
                alert('Teste salvo com sucesso!');
                loadTests();
                $('#newTestBtn').click();
            }
        },
        error: function() {
            alert('Erro ao salvar o teste.');
        }
    });
}

function getSteps() {
    const steps = [];
    $('.step-item').each(function() {
        steps.push({
            description: $(this).find('.step-description').val(),
            status: $(this).find('.step-status').val(),
            details: $(this).find('.step-details').val()
        });
    });
    return steps;
}

function getEnvironment() {
    const env = {};
    $('.env-item').each(function() {
        const key = $(this).find('.env-key').val();
        const value = $(this).find('.env-value').val();
        if (key && value) {
            env[key] = value;
        }
    });
    return env;
}

function getCustomFields() {
    const fields = {};
    $('.custom-field-item').each(function() {
        const name = $(this).find('.custom-field-name').val();
        const value = $(this).find('.custom-field-value').val();
        if (name && value) {
            fields[name] = value;
        }
    });
    return fields;
}

function loadTestDetails(testId) {
    // Implementar carregamento dos detalhes do teste
    // Esta função será implementada quando adicionarmos a rota de API correspondente
} 